import apsw
import utilities.fileio as fo
import utilities.pairings as pairings

from modules.queries import score_card_query
import modules.club as club

connection = apsw.Connection("data/dbfile.db")


def check_for_end_of_round(group_id):
    # get current round number for group
    cursor = connection.cursor()
    round_number = list(
        cursor.execute(
            f'SELECT round_number FROM groups \
            WHERE id={group_id}'
        )
    )[0][0]

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
    end_of_round = False
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
    if (round_number == 5 and pairing_method == 1) or (round_number == 3 and pairing_method == 2):
        end_of_round, round_number = check_for_end_of_round(group_id)
    message = f'```\nRESULT #{result_id}:\n{p1} {s1} {p2} {s2}\n```'
    return message, end_of_round, round_number, group_id


def save(format, date):
    return


def get_player_last_game(name, rnd=1):

    return msg, pairing_message, quackle


def delete_result(id_number):
    cursor = connection.cursor()
    cursor.execute(f'DELETE FROM results WHERE id={id_number}')
    msg = f'{id_number} deleted'
    return msg


def show_summary():
    cards = get_scorecards()
    # name,win score,win opp score,lose score,lose opp score,total spread, wins, group, #games,
    msgs = ["{:>5}{:>15}{:>5}{:>5}{:>5}{:>5}\n\n".format(
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
                    f'{name:>15}'
                    f'{wins:>5}'
                    f'{spread:>5}'
                    f'{average:>5}'
                    f'{high_game:>5}'
                    )

    return '\n'.join(msgs)


def get_results():

    return msg


def get_scorecards():
    event_id, _ = club.get_event()
    cursor = connection.cursor()
    sc = list(cursor.execute(score_card_query(event_id)))
    columns = ['group_number','round_number','max', 'average','player_id', 
'full_name', 'group_id', 'byes', 'spread', 'wins', 'games','rating']
    # return list of players scorecards
    # [{"player_id": 15, "full_name": "Danielle Barker",
    # "wins": 3.5, "spread": +124, "byes": 1}, ...]
    return fo.query_to_dict_array(columns, sc)


def get_pairings(round_number, group_id):

    return pairings.get_pairings_text(
        round_number, group_id, get_scorecards())
