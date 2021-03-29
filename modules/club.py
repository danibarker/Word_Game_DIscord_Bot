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
    '''
    adds an event into the db with a pairing
    method based on the day of the week
    returns None
    '''

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


def get_event(event_date=None):
    '''
    returns event id for the current event
    creates a new event if a date is not specified
    or event for today does not exist
    '''

    cursor = connection.cursor()
    date = event_date or time.strftime('%Y-%m-%d')
    if not event_date:
        create_event()

    m = list(cursor.execute(
        f"SELECT id, pairing_method FROM events WHERE date = '{date}'"))
    return m[0]


def find_player_id(query):
    '''
    finds a player id from the database
    takes in a string that will match either
    discord id, isc username, or full_name

    returns the id found
    '''
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
    raise AmbiguousRequest(
        f'Please be more specific,\
            {query} matched more than one player')


def sign_in(player):
    '''
    adds a player to the event attendees table in the db
    takes in a string that can be their name, isc username,
    discord username, as long as it is specific enough

    returns a message saying the player has signed in or
    an error message if player doesn't exist in db or 
    matched more than one player
    '''
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
    '''
    removes a player from the event_attendees table
    in the db.

    takes a string representing all or part of full name,
    discord username, isc username

    returns a message saying they were signed out
    or an error if that player was not found
    or query was not specific enough
    '''
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
    '''
    gets the players in the event attendees table
    in the db for the current event.

    returns an array of dicts, one for each player
    '''
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
    columns = ['id', 'first_name', 'last_name', 'discord', 'isc',
               'abbreviation', 'rating', 'rung', 'full_name', 'current_opponent']
    return fo.query_to_dict_array(columns, players)


def get_attendance():
    '''
    gets the players currently signed in and
    formats the list

    returns a string
    '''
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
    '''
    updates event_attendees table setting the bye column to the round
    that the player is assigned to
    returns a string listing the byes
    '''
    cursor = connection.cursor()

    byes = random.sample(groups[bye_group_number], num_of_byes)
    for i, player in enumerate(byes):
        cursor.execute(f'UPDATE event_attendees SET bye = {i+1} \
       WHERE player_id = {player["id"]}')

    msg = f"Byes: {', '.join(player['discord'] for player in byes)}\n"
    return msg


def set_player_groups(group, group_number, event_id):
    '''
    updates the db adding a group of the given group of players
    takes in an array of player dicts, a group number,
    and an event id

    returns the newly created group record's id
    '''
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
        VALUES({value_list}) ')
    return group_id


def create_groups(event_id):
    '''
    groups players that are signed in to a particular event
    returns a string containing the list of players by group
    and a list of group ids
    '''
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

    group_ids = []
    for i, group in enumerate(groups):
        group_number = i + 1
        group_id = set_player_groups(group, group_number, event_id)
        group_ids.append(group_id)
        msg += f"Group {group_number} \
        {', '.join(player['full_name'] for player in group)}\n"
    msg += bye_message
    return msg, group_ids


def start_event():
    '''
    starts an event
    returns a string containing the list of groups
    and each player in those groups and a list of 
    associated group ids from the db
    '''
    event_id, pairing_method = get_event()
    cursor = connection.cursor()
    players_query = cursor.execute(
        f'SELECT p.* FROM event_attendees e INNER JOIN players p \
            ON e.player_id = p.id \
            WHERE e.event_id = {event_id}'
    )
    columns = ['id', 'first_name', 'last_name', 'discord', 'isc',
               'abbreviation', 'rating', 'rung', 'full_name', 'current_opponent']
    players = fo.query_to_dict_array(columns, players_query)
    if pairing_method == 2:
        msg, group_ids = create_groups(event_id)
    elif pairing_method == 1:
        group_ids = [set_player_groups(players, 1, event_id)]
        if len(players) % 2 == 1:
            bye_message = set_byes([players], 5)
            msg = bye_message
        else:
            msg = ""
    msg = "Event Started\n" + msg
    return msg, group_ids
