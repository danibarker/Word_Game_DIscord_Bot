from urllib.request import urlopen
import apsw
import json

from utilities.scrabble_classes import player_decoder, results_decoder

connection = apsw.Connection("data/dbfile.db")

def query_to_dict_array(columns, results):
    print(columns, 'columns',results,'results')
    new_array = []
    for item in results:
        print(item,'item')
        new_dict = {}
        for i, column in enumerate(item):
            new_dict[columns[i]] = column if column else 0
        new_array.append(new_dict)
    return new_array

def get_player_ratings(players, province='AB'):
    
    """
    Go out to crosstables, get player ratings in specified province (or state) (2 letter abbrev)
    Write it back to disk.

    """

    url = f'https://www.cross-tables.com/bystate.php?st={province}&who=all'
    with urlopen(url) as response:
        js = response.read().decode('utf-8').upper()
    for p in players:
        start = js.find('TDR\'>', js.find(p.full_name.upper())) + 5
        if start != 4:
            try:
                p.rating = int(js[start:start + 4].strip('&* '))
                print(f'{p.full_name} found, rating = {p.rating}')
            except ValueError:

                print(p.full_name + " error")

        else:
            print(f'{p.full_name} not found on cross-tables in {province}')
def update_player_rungs():
    """
    Go out to the club website, read the latest rungs that people are on
    (this information is updated every Thursday after a club session)
    and update the players table.

    Example line in the json array: 
    [{"ranking": "59",
     "player_name": "Linda Slater",
      "the_date": "2020-04-16"},...] 
    """

    url = "http://www.calgary374.org/json/ladder.php"
    with urlopen(url) as response:
        js = response.read()

    data = json.loads(js)

    msg = ""
    for d in data:
        try:
            new_rung = int(d["ranking"])
            name = d['player_name']
            cursor = connection.cursor()
            cursor.execute(f"UPDATE players SET rung={new_rung} \
            WHERE first_name || ' ' || last_name = '{name}'")
            msg += f"Updated {new_rung}, {name}\n"
        except Exception as e:
            print(e)
            msg = 'Something went wrong'
    return msg
