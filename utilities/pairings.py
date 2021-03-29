from itertools import combinations
import apsw
import networkx as nx
from functools import reduce
import modules.club as club

connection = apsw.Connection("data/dbfile.db")


def get_first_pairings():
    if pairing_method == 2:
        return pairings_group_round1()

    return pairings_swiss()


def set_opponents(p1, p2):
    cursor = connection.cursor()
    cursor.execute(f'UPDATE players SET current_opponent = {p1} WHERE id = {p2};\
        UPDATE players SET current_opponent = {p2} WHERE id = {p1};')


def get_pairings_text(_round_number, _group_id, _score_cards):
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
        ORDER BY l.rating desc')]
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


def pairings_group_round1():

    num_pairs = len(players_in_group) // 2
    pairs = []
    for p in range(num_pairs):
        pairs.append(
            (players_in_group[2 * p], players_in_group[2 * p + 1]))
    return pairs


def get_past_opponents(player_id):
    cursor = connection.cursor()
    return cursor.execute(f'SELECT player1 FROM results \
        WHERE player2={player_id} AND event_id={event_id} \
            UNION\
        SELECT player2 FROM results \
            WHERE player1={player_id} and event_id={event_id}')


def pairings_koth(avoid_repeats=True):
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
        player_1_win_spread = players_list[p1][0] * 10000 + players_list[p1][1]
        player_2_win_spread = players_list[p2][0] * 10000 + players_list[p2][1]
        if not avoid_repeats:
            played_together = 0
        else:
            try:
                played_together = -1000000.0 * past_matches[f'{p1}-{p2}']
            except KeyError:
                pass

        adjustment = players_list[p1][2] * \
            (players_list[p1][2] - players_list[p2][2])
        weight_value = played_together - adjustment * \
            (abs(player_2_win_spread - player_1_win_spread)) + 50000000

        network.add_edge(p1, p2, weight=weight_value)
    result = nx.algorithms.max_weight_matching(network, maxcardinality=True)
    return result


def format_pairings(pairs):
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
    # This is hardcoded to assume swiss pairings will only be used for the first round.
    # it simply chops the list in two [A1..An] and [B1..Bn], by rating where
    # the A's are the top half and the B's are the bottom half.
    # It then pairs A1 vs B1, A2 vs B2, ..., An vs Bn.

    attendees = players_in_group

    assert len(attendees) % 2 == 0

    n = len(attendees) // 2

    part1 = attendees[:n]  # Top half
    part2 = attendees[n:]  # Bottom half

    pairs = []
    for (p1, p2) in zip(part1, part2):
        pairs.append((p1.name, p2.name))

    return pairs
