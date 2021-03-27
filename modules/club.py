import random
import re
import time
import utilities.isc_scraper as isc
import utilities.pairings as pairings
import utilities.scrabble_classes as sc
import utilities.fileio as io
import json
import apsw
from urllib.request import urlopen
from exceptions.exceptions import *
connection=apsw.Connection("dbfile")

f = open("data/config.dat", 'r')
bot_token = f.readline().strip()
f.close()
def create_event():
    day = time.strftime('%A')
    date = time.strftime('%Y-%m-%d')
    if day == 'Friday':
        pairing_method = 2
    else:
        pairing_method = 1
    cursor=connection.cursor()
    
    print(day)
    sql = f"INSERT OR IGNORE INTO events(date, pairing_method) \
    VALUES ('{date}', {pairing_method})"
    cursor.execute(sql)
    

def get_event():
    cursor=connection.cursor()
    date = time.strftime('%Y-%m-%d')
    create_event()
    
    m = list(cursor.execute(f"SELECT id, pairing_method FROM events \
    WHERE date = '{date}'"))
    print('event',m)
    return m[0]
def get_player_by_discord(discord):
    cursor=connection.cursor()
    print('discord',discord)
    id_query = list(cursor.execute(f"SELECT id FROM players \
    WHERE UPPER(discord) = '{discord}'"))
    if len(id_query) >= 1:
        id = id_query[0][0]
        return id
   
    raise PlayerDoesntExist('Player does not exist, use discord username')
    

def sign_in(player):
    try:
        event_id = get_event()[0]
        player_id = get_player_by_discord(player)
        cursor=connection.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO \
        event_attendees(player_id, event_id) VALUES ({player_id},{event_id})")
        msg = f'{player} signed in'
    except PlayerDoesntExist as e:
        print(e)
        msg = e
    return msg


def sign_out(player):
    try:
        event_id = get_event()[0]
        player_id = get_player_by_discord(player)
        cursor=connection.cursor()
        cursor.execute(f"DELETE from event_attendees \
        WHERE player_id={player_id} AND event_id={event_id}")
        msg = f'{player} signed out'
    except PlayerDoesntExist as e:
        print(e)
        msg = e
    return msg


def query_to_dict_array(cursor, results):
    columns = cursor.getdescription()
    new_array = []
    for item in results:
        new_dict = {}
        for i,column in enumerate(item):
            new_dict[columns[i][0]] = column
        new_array.append(new_dict)
    return new_array


def get_players():
    event_id, pairing_method = get_event()
    cursor=connection.cursor()
    if pairing_method == 1:
        players = cursor.execute(f"SELECT p.* \
        FROM event_attendees e INNER JOIN players p \
        ON e.player_id = p.id WHERE event_id = {event_id} \
        ORDER BY p.rating")
    elif pairing_method == 2:
        players = cursor.execute(f"SELECT p.* \
        FROM event_attendees e INNER JOIN players p \
        ON e.player_id = p.id WHERE event_id = {event_id} \
        ORDER BY p.rung")
    return query_to_dict_array(cursor, players)

def get_attendance():
    try:
        players = get_players()
        print(players)
        msg = ','.join([player['first_name'] for player in players])
    except Exception as e:
        print(e)
        msg = 'Something went wrong'
    return msg

def set_byes(groups, num_of_byes, bye_group_number):
    cursor = connection.cursor()
    
    
    byes = random.sample(groups[bye_group_number], num_of_byes)
    print('byes',byes)
    for i,player in enumerate(byes):
        cursor.execute(f'UPDATE event_attendees SET bye = {i+1} WHERE player_id = {player["id"]}')
        
    msg = f"Byes: {', '.join(player['discord'] for player in byes)}\n"
    return msg

def set_player_groups(group, group_number, event_id):
    cursor=connection.cursor()
    
    for player in group:
        print('this is the player',player)
        player_id = player['id']
        value_list = f'{group_number},{event_id},{player_id},1' 
        cursor.execute(f'REPLACE INTO \
        player_groups(group_number, event_id, player_id, round_number) \
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
        bye_message = set_byes(groups, 3,bye_group_number)
    for i,group in enumerate(groups):
        group_number = i + 1
        set_player_groups(group, i, event_id)
        
        msg += f"Group {group_number} {', '.join(player['first_name'] + ' ' + player['last_name'] for player in group)}\n"
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
    players = query_to_dict_array(cursor,players_query)
    if pairing_method == 2:
        msg += create_groups(event_id)
    elif pairing_method == 1:
        set_player_groups(players,1,event_id)
        if len(players) % 2 == 1: 
            bye_message = set_byes([players], 5)
            msg += bye_message
    return msg 


def parse_result(s):
    
    return message, pairing_message


def get_next_result_id():
    
    return result_id


def next_round(group=0):
    
    return group, pairing_message


def prev_round(group=0):
    
    return group, group_round_number[group]


def delete_result(id_number):
    
    return msg


def show_summary():
    
    return '\n'.join(msgs)


def get_results():
    
    return msg


def pairings_text():
    return pairings.get_pairings_text(group_round_number[0], get_scorecards(), players, byes, False, bye_group_number == 0)


def get_scorecards():
    
    return cards


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def save(format,date):
    return
def reset():
    return

def get_player_last_game(name,rnd=1):
    
    return msg, pairing_message, quackle

def get_last_games():
    
    return msgs, pairing_message

def update_player_rungs():
    """
    Go out to the club website, read the latest rungs that people are on
    (this information is updated every Thursday after a club session)
    and update the players table.
    """
    

    url = "http://www.calgary374.org/json/ladder.php"
    with urlopen(url) as response:
        js = response.read()

    # Example line in the json array: [{"ranking": "59", "player_name": "Linda Slater", "the_date": "2020-04-16"},...]
    data = json.loads(js)

    
    msg = ""
    for d in data:
        try:
            new_rung = int(d["ranking"])
            name = d['player_name']
            cursor=connection.cursor()
            cursor.execute(f"UPDATE players SET rung={new_rung} \
            WHERE first_name || ' ' || last_name = '{name}'")
            msg += f"Updated {new_rung}, {name}\n"
        except Exception as e:
            print(e)
            msg = 'Something went wrong'
    return msg
    
       
       