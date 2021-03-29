import apsw
import utilities.fileio as fo
import utilities.pairings as pairings

from modules.queries import score_card_query
import modules.club as club

connection = apsw.Connection("data/dbfile.db")


def check_for_end_of_round(group_id, pairing_method):
    '''
    accesses the db to calculate if a round is over
    besed on number of results and
    number of players in the group

    takes a group id and a pairing method
    returns 2 values, a boolean representing if the round is over
    and the round number the group is now on
    '''

    cursor = connection.cursor()

    # get current round number for particular group id
    round_number = list(
        cursor.execute(
            f'SELECT round_number FROM groups \
            WHERE id={group_id}'
        )
    )[0][0]

    if (round_number == 5 and pairing_method == 1) or (round_number == 3 and pairing_method == 2):
        # last round of the event
        return False, round_number
    # count number of results with that group and round
    number_of_results = list(
        cursor.execute(
            f'SELECT COUNT(1) FROM results \
            WHERE round={round_number} AND group_id={group_id} '
        )
    )[0][0]

    # check number of players in group
    players_in_group = list(
        cursor.execute(
            f'SELECT COUNT(1) FROM player_groups \
            WHERE group_id={group_id} '
        )
    )[0][0]
    if number_of_results == players_in_group//2:
        cursor.execute(
            f'UPDATE groups SET round_number = {round_number+1}\
            WHERE id = {group_id}')

        return True, round_number + 1
    return False, round_number


def parse_result(s):
    '''
    enters a result into the database and
    checks if the round is over

    takes a string as input, formatted:
    "player1 score1 player2 score2"

    returns a message string with the result, 
    boolean for if a round is over, 
    updated round number
    and group_id
    '''

    event_id, pairing_method = club.get_event()
    p1, s1, p2, s2 = s.split(' ')

    player1 = club.find_player_id(p1)
    player2 = club.find_player_id(p2)
    score1 = s1
    score2 = s2
    # player with lower id is player 1 to prevent possible duplicate results
    if player2 < player1:
        player1, score1, player2, score2 = player2, score2, player1, score1

    cursor = connection.cursor()
    group_id_query = f'SELECT group_id FROM player_groups WHERE \
        event_id = {event_id} AND player_id = {player1}'

    group_id = list(cursor.execute(group_id_query))[0][0]

    enter_result_query = f'REPLACE INTO results (score_1, score_2, \
        player1, player2, round, group_id, event_id) \
        VALUES ({score1},{score2},{player1},{player2},\
        (SELECT round_number FROM groups WHERE id=\
        {group_id}), {group_id}, {event_id});'

    cursor.execute(enter_result_query)
    result_id = list(
        cursor.execute(f'SELECT id FROM results WHERE player1 = {player1} \
        AND player2={player2} AND round=\
        (SELECT round_number FROM groups WHERE id=\
        {group_id}) and event_id={event_id} ')
    )[0][0]

    end_of_round, round_number = check_for_end_of_round(
        group_id, pairing_method)
    message = f'```\nRESULT #{result_id}:\n{p1} {s1} {p2} {s2}\n```'
    return message, end_of_round, round_number, group_id


def save():
    '''
    sends results to calgary374.org
    '''
    return


def get_player_last_game(name, rnd=1):
    '''
    connect to ISC get result of a given players match
    converts result to string for parse_result function
    returns a message string with the result, 
    boolean for if a round is over, 
    updated round number and group_id
    '''
    return msg, end_of_ound, round_number, group_id


def delete_result(id_number):
    '''
    deletes a result from the database
    takes a result id
    returns a string saying it was deleted
    '''
    cursor = connection.cursor()
    cursor.execute(f'DELETE FROM results WHERE id={id_number}')
    msg = f'{id_number} deleted'
    return msg


def show_summary(event_date=None):
    '''
    gets scorecards for a particular event date
    or the current event if None and formats
    them into a string

    returns the results summary string
    '''

    cards = get_scorecards(event_date)
    # name,win score,win opp score,lose score,lose opp score,total spread, wins, group, #games,
    msgs = ["{:>5}{:>20}{:>12}{:>12}{:>12}{:>12}\n\n".format(
        "GROUP", "NAME", "WINS", "SPREAD", "AVERAGE", "HIGH"
    )]

    for sc in cards:

        name = sc['full_name']
        spread = sc['spread']
        wins = sc['wins']
        games = sc['games']
        group = sc['group_number']
        average = sc['average']
        high_game = sc['max']

        msgs.append(f'{group:>5}'
                    f'{name:>20}'
                    f'{wins:>12}'
                    f'{spread:>12}'
                    f'{average:>12}'
                    f'{high_game:>12}'
                    )

    return '\n'.join(msgs)


def get_results(event_date=None):
    '''
    gets list of results from the database
    for a particular event
    and formats them into a string
    '''

    return msg


def get_scorecards(event_date=None):
    '''
    gets scorecards from the database
    for a particular event date
    returns list of players scorecards
    [{'group_number':1,'round_number':2,'max':500, 'average':435,'player_id':15, 
    'full_name':"Danielle Barker", 'group_id':17, 'byes':1, 'spread':765, 
    'wins':3, 'games':5,'rating':940}, ...]
    '''

    event_id, _ = club.get_event(event_date)
    cursor = connection.cursor()
    sc = list(cursor.execute(score_card_query(event_id)))
    columns = ['group_number', 'round_number', 'max', 'average', 'player_id',
               'full_name', 'group_id', 'byes', 'spread', 'wins', 'games', 'rating']

    return fo.query_to_dict_array(columns, sc)


def get_pairings(round_number, group_id):
    '''
    returns text containing pairing for a given round
    number and group id for the current event
    '''
    return pairings.get_pairings_text(
        round_number, group_id, get_scorecards())
