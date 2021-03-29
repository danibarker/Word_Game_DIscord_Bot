from itertools import combinations
import apsw
import networkx as nx
from functools import reduce
import modules.club as club

connection = apsw.Connection("data/dbfile.db")


def get_pairings_text(_round_number, _group_id, _score_cards):
    '''
    returns formatted pairings for a particular round for a particular group.
    declares global variables that the other functions in this file use.
    takes in a round number: int, group id: int, 
    and score card for the current event: array of dicts.
    returns a string
    '''
    global round_number, group_id, event_id, pairing_method, players_in_group
    global score_cards
    score_cards = _score_cards
    round_number = _round_number
    group_id = _group_id
    event_id, pairing_method = club.get_event()
    cursor = connection.cursor()

    players_in_group = [p[0] for p in cursor.execute(
        f'SELECT e.player_id FROM event_attendees e \
        INNER JOIN player_groups p ON p.player_id=e.player_id \
        INNER JOIN players l ON l.id=p.player_id \
        WHERE(bye <> 1 or bye IS NULL) AND p.group_id={group_id}\
        AND e.event_id = {event_id} ORDER BY l.rating desc')]
    if round_number <= 1:
        pairs = get_first_pairings()
    elif round_number <= 4:
        pairs = pairings_koth(avoid_repeats=True)
    else:
        pairs = pairings_koth(avoid_repeats=False)

    header = f"ROUND {round_number}"
    for pair in pairs:
        p1 = pair[0]
        p2 = pair[1]
        set_opponents(p1, p2)

    body = format_pairings(pairs)
    text = header + "\n" + body

    return text


def get_first_pairings():
    '''
    returns pairings for round 1 based on pairing method
    method 1 is Open 5 Rounds
    method 2 is Ladder 3 Rounds
    '''
    if pairing_method == 2:
        return pairings_group_round1()

    return pairings_swiss()


def pairings_group_round1():
    '''
    creates pairings for round 1 of a ladder event
    returns an array of tuples containing player ids
    matched p1 v p2, p3 v p4, ...
    '''
    num_pairs = len(players_in_group) // 2
    pairs = []
    for p in range(num_pairs):
        pairs.append(
            (players_in_group[2 * p], players_in_group[2 * p + 1]))
    return pairs


def pairings_koth(avoid_repeats=True):
    '''
    calculates weighted pairings based on wins and spread 
    with a tie breaker of higher rated players playing together.

    avoid_repeats flag is standard and negatively weights pairs that
    have played together in previous rounds it is
    turned off for final round of Open 5 rounds.

    returns the highest weighted combination of pairings
    as a tuple of tuples each containing a pairing.
    '''
    past_matches = {}
    players_list = {}
    network = nx.Graph()
    correction = len(players_in_group) + 1

    cards_by_id = dict([(x['player_id'], x) for x in score_cards])
    for player_id in players_in_group:
        for match in get_past_opponents(player_id):
            try:
                past_matches[f'{match[0]}-{player_id}'] += 1
                past_matches[f'{player_id}-{match[0]}'] += 1
            except KeyError:
                past_matches[f'{match[0]}-{player_id}'] = 1
                past_matches[f'{player_id}-{match[0]}'] = 1

        correction -= 1
        players_list[player_id] = [cards_by_id[player_id]['wins'],
                                   cards_by_id[player_id]['spread'], correction]

    for (p1, p2) in combinations(players_list, 2):
        # wins * 100000  + spread
        player_1_win_spread = players_list[p1][0] * 10000 + players_list[p1][1]
        player_2_win_spread = players_list[p2][0] * 10000 + players_list[p2][1]
        if not avoid_repeats:
            played_together = 0
        else:
            try:
                # -20000000 for each time they played together, most significant adjustment
                played_together = -1000000.0 * past_matches[f'{p1}-{p2}']
            except KeyError:
                played_together = 0
        # in case of ties, adjustment is position in list by rating * the difference in the position
        # for a group of 10, this will be 90 at the most, least significant adjustment
        adjustment = players_list[p1][2] * \
            (players_list[p1][2] - players_list[p2][2])

        # total weight value gets 50,000,000 added to it, because max_weight_matching needs a positive number
        weight_value = played_together - \
            abs(player_2_win_spread - player_1_win_spread) - \
            adjustment + 50000000

        network.add_edge(p1, p2, weight=weight_value)

    result = nx.algorithms.max_weight_matching(network, maxcardinality=True)

    return result


def get_past_opponents(player_id):
    '''
    accesses the db and gets back a list of past opponents
    given a particular player id for the current event
    returns an APSW cursor (iterable)
    '''
    cursor = connection.cursor()
    return cursor.execute(f'SELECT player1 FROM results \
        WHERE player2={player_id} AND event_id={event_id} \
            UNION\
        SELECT player2 FROM results \
            WHERE player1={player_id} and event_id={event_id}')


def format_pairings(pairs):
    '''
    formats pairings from a list of tuples of player ids
    returns a string
    '''
    cards_by_id = dict([(x['player_id'], x) for x in score_cards])

    def fmtp(name):
        p = cards_by_id[name]
        return "**%s** (%d) (%.1lf-%.1lf %+d)" % (p['full_name'].lower(), p['rating'], p['wins'], p['games']-p['wins'], p['spread'])

    def scoreOf(name):
        p = cards_by_id[name]
        return p['wins']+0.5*p['byes'], p['spread'], p['rating']

    def scoreOf2(pair):
        [p1, p2] = pair
        m1 = sorted([scoreOf(p1), scoreOf(p2)], reverse=True)
        return m1

    ps = list(pairs)

    # Sort list so highest scoring players are on top.
    ps.sort(reverse=True, key=scoreOf2)
    # Sort each pair so best player is listed first.
    ps = [list(sorted(pair, reverse=True, key=scoreOf)) for pair in ps]

    lines = [" %s vs. %s" % (fmtp(p1), fmtp(p2)) for (p1, p2) in ps]

    # If there is a bye, show it.
    cursor = connection.cursor()
    bye = list(cursor.execute(f'SELECT p.isc FROM event_attendees e \
        INNER JOIN players p ON p.id=e.player_id\
        WHERE event_id = {event_id} AND bye = {round_number}'))
    if len(bye) > 0:
        lines.append(" **%s** BYE" % bye[0][0])

    msg = "\n".join(lines)
    return msg


def pairings_swiss():
    '''
    This is hardcoded to assume swiss pairings will only be used for the first round.
    it simply chops the list in two [A1..An] and [B1..Bn], by rating where
    the A's are the top half and the B's are the bottom half.
    It then pairs A1 vs B1, A2 vs B2, ..., An vs Bn.
    returns an array of tuples, each containing a pairing
    '''
    attendees = players_in_group
    print(attendees)
    assert len(attendees) % 2 == 0

    n = len(attendees) // 2

    part1 = attendees[:n]  # Top half
    part2 = attendees[n:]  # Bottom half
    print(part1, part2)
    pairs = []
    for (p1, p2) in zip(part1, part2):
        pairs.append((p1, p2))

    return pairs
