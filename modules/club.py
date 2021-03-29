from urllib.request import urlopen
import apsw
import json
import random
import re
import time

from exceptions.exceptions import *
import utilities.fileio as fo
import utilities.isc_scraper as isc

connection = apsw.Connection("data/dbfile.db")

f = open("data/config.dat", 'r')
bot_token = f.readline().strip()
f.close()


def create_event():
    day = time.strftime('%A')
    date = time.strftime('%Y-%m-%d')
    if day == 'Thursday':
        pairing_method = 2
    else:
        pairing_method = 1
    cursor = connection.cursor()

    sql = f"INSERT OR IGNORE INTO events(date, pairing_method) \
        VALUES ('{date}', {pairing_method})"
    cursor.execute(sql)


def get_event():
    cursor = connection.cursor()
    date = time.strftime('%Y-%m-%d')
    create_event()

    m = list(cursor.execute(
        f"SELECT id, pairing_method FROM events WHERE date = '{date}'"))
    return m[0]


def find_player_id(query):
    cursor = connection.cursor()
    player_query = list(cursor.execute(
        f"SELECT id FROM players WHERE UPPER(discord) LIKE '%{query}%' OR \
        UPPER(isc) LIKE '%{query}%' OR UPPER(full_name) LIKE '%{query}%'"
    ))
    if len(player_query) == 1:
        id = player_query[0][0]
        return id
    if len(player_query) == 0:
        raise PlayerDoesntExist('Player does not exist, use discord username')
    else:
        raise AmbiguousRequest(
            f'Please be more specific, \
            {query} matched more than one player')


def sign_in(player):
    try:
        event_id = get_event()[0]
        player_id = find_player_id(player)
        cursor = connection.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO \
        event_attendees(player_id, event_id) VALUES ({player_id},{event_id})")
        msg = f'{player} signed in'
    except PlayerDoesntExist as e:
        print(e)
        msg = e
    except AmbiguousRequest as e:
        msg = e
    return msg


def sign_out(player):
    try:
        event_id = get_event()[0]
        player_id = find_player_id(player)
        cursor = connection.cursor()
        cursor.execute(f"DELETE from event_attendees \
        WHERE player_id={player_id} AND event_id={event_id}")
        msg = f'{player} signed out'
    except PlayerDoesntExist as e:
        print(e)
        msg = e
    return msg


def get_players():
    event_id, pairing_method = get_event()
    cursor = connection.cursor()
    if pairing_method == 1:
        players = cursor.execute(f"SELECT p.* \
        FROM event_attendees e INNER JOIN players p \
        ON e.player_id = p.id WHERE event_id = {event_id} \
        ORDER BY p.rating DESC ")
        
    elif pairing_method == 2:
        players = cursor.execute(f"SELECT p.* \
        FROM event_attendees e INNER JOIN players p \
        ON e.player_id = p.id WHERE event_id = {event_id} \
        ORDER BY p.rung ")
    columns = ['id','first_name','last_name','discord','isc','abbreviation','rating','rung','full_name','current_opponent']
    return fo.query_to_dict_array(columns, players)


def get_attendance():
    try:
        players = get_players()
        msg = f'```\n{len(players)} players signed in'
        for i, player in enumerate(players):
            msg += '{0: <20}\t{1: <12}\t{2: <8}'.format(f'\n\t{i+1}. {player["full_name"]}',
                                                        f'rating: {player["rating"]}',
                                                        f'rung: {player["rung"]}')
        msg += '\n```'
    except Exception as e:
        print(e)
        msg = 'Something went wrong'
    return msg


def set_byes(groups, num_of_byes, bye_group_number):
    cursor = connection.cursor()

    byes = random.sample(groups[bye_group_number], num_of_byes)
    for i, player in enumerate(byes):
        cursor.execute(f'UPDATE event_attendees SET bye = {i+1} \
       WHERE player_id = {player["id"]}')

    msg = f"Byes: {', '.join(player['discord'] for player in byes)}\n"
    return msg


def set_player_groups(group, group_number, event_id):
    cursor = connection.cursor()
    cursor.execute(f'REPLACE INTO groups (event_id, group_number, round_number) \
    VALUES({event_id},{group_number},1)')
    group_id_query = cursor.execute(f'SELECT id FROM groups \
    WHERE event_id = {event_id} \
    AND group_number = {group_number}')
    group_id = list(group_id_query)[0][0]
    for player in group:
        player_id = player['id']
        value_list = f'{group_id},{player_id},{event_id}'
        cursor.execute(f'REPLACE INTO \
        player_groups(group_id, player_id, event_id) \
        VALUES({value_list})')


def create_groups(event_id):
    players = get_players()
    num_players = len(players)
    bye_message = ''
    msg = ''
    number_of_groups = num_players // 4 + (1 if num_players % 4 == 3 else 0)
    distribution = num_players % 4

    group_sizes = [4 for _ in range(number_of_groups)]
    bye_group_number = random.randint(0, number_of_groups - 1)
    if distribution == 1:  # bye group has 5 players
        group_sizes[bye_group_number] = 5

    elif distribution == 2:  # no byes, group of 6
        group_sizes[random.randint(0, number_of_groups - 1)] = 6

    elif distribution == 3:  # bye group has 3 players

        group_sizes[bye_group_number] = 3

    elif num_players == 2:  # group of 2
        group_sizes = [2]
    else:  # all groups of 4
        pass
    groups = []

    for (i, k) in enumerate(group_sizes):
        group = players[:k]  #
        players = players[k:]  # Throw the first k out.
        groups.append(group)

    if distribution % 2 == 1:
        bye_message = set_byes(groups, 3, bye_group_number)
    for i, group in enumerate(groups):
        group_number = i + 1
        set_player_groups(group, group_number, event_id)

        msg += f"Group {group_number} \
        {', '.join(player['full_name'] for player in group)}\n"
    msg += bye_message
    return msg


def start_event(given_byes=()):
    msg = "Event Started\n"
    event_id, pairing_method = get_event()
    cursor = connection.cursor()
    players_query = cursor.execute(
        f'SELECT p.* FROM event_attendees e INNER JOIN players p \
            ON e.player_id = p.id \
            WHERE e.event_id = {event_id}'
    )
    columns = ['id','first_name','last_name','discord','isc','abbreviation','rating','rung','full_name','current_opponent']
    players = fo.query_to_dict_array(columns, players_query)
    if pairing_method == 2:
        msg += create_groups(event_id)
    elif pairing_method == 1:
        set_player_groups(players, 1, event_id)
        if len(players) % 2 == 1:
            bye_message = set_byes([players], 5)
            msg += bye_message
    return msg
