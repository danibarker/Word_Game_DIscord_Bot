import os
import copy
import modules.club as club
import modules.dictionary as dic
import json
bingos = []
phonies = []
max_score = 0
max_word = ''
max_player = ''
player_bingos = {}
tiles_played= {}
class Game():
    def __init__(self):
        self.state = [['.' for i in range(15)] for i in range(15)]
        self.moves = []
        self.racks = []
        self.tiles_not_on_board = {
            'A':9,
            'B':2,
            'C':2,
            'D':4,
            'E':12,
            'F':2,
            'G':3,
            'H':2,
            'I':9,
            'J':1,
            'K':1,
            'L':4,
            'M':2,
            'N':6,
            'O':8,
            'P':2,
            'Q':1,
            'R':6,
            'S':4,
            'T':6,
            'U':4,
            'V':2,
            'W':2,
            'X':1,
            'Y':2,
            'Z':1,
            '?':2
                        }
def move(board,row,column,word,orientation,player):
    global plain_word
    tiles_played = []
    row = row-1
    column = column-1
        
    if orientation == 1:
            
        for n,y in enumerate(range(row,row+len(word))):
            if board[column][y] == '.' or board[column][y] == word[n]:
                if not board[column][y] == word[n]:
                    tiles_played.append(word[n])
                board[column][y] = word[n]
                
            else:
                return False, None
        for tile in tiles_played:
            game.tiles_not_on_board[tile]-=1
        if len(tiles_played)==7:
            if plain_word not in dic.TWL:
                plain_word = plain_word+"*"
            bingos.append(plain_word)
            try:
                player_bingos[player].append(plain_word)
            except:
                player_bingos[player]=[]
                player_bingos[player].append(plain_word)

        if plain_word not in dic.TWL:
            phonies.append(plain_word)
        return True,tiles_played         
                    
    if orientation == 0:
            
        for n,x in enumerate(range(column,column+len(word))):
            if board[x][row] == '.' or board[x][row] == word[n]:
                if not board[x][row] == word[n]:
                    tiles_played.append(word[n])
                board[x][row] = word[n]
            else:
                   
                return False, None
        for tile in tiles_played:
            game.tiles_not_on_board[tile]-=1  
        if len(tiles_played)==7:
            if plain_word not in dic.TWL:
                plain_word = plain_word+"*"
            bingos.append(plain_word)
            try:
                player_bingos[player].append(plain_word)
            except:
                player_bingos[player]=[]
                player_bingos[player].append(plain_word)
        if plain_word not in dic.TWL:
            phonies.append(plain_word)
        return True, tiles_played
def move_input(board,play,player):
    global plain_word
    row_conv = '.ABCDEFGHIJKLMNO'
    word = play[1]
    plain_word = word.upper()
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        
        word = word.replace(letter,'?') #convert blanks to ?
    word = word.upper()
    
    position = play[0]
    if position[0].isalpha():
        row = row_conv.index(position[0])
        column= int(position[1:])
        orientation = 0
    else:
        column = int(position[:-1])
        row = row_conv.index(position[-1:])
        orientation = 1
    return move(board,row,column,word,orientation,player)
def move_list(game,moves_raw):
    global max_player,max_score,max_word
    player = ''
    try:
        tiles_played[moves_raw.split('\n')[1].split()[1]]['games_played']+=1
        
    except:
        tiles_played[moves_raw.split('\n')[1].split()[1]] = {'games_played':1}
    try:
        tiles_played[moves_raw.split('\n')[2].split()[1]]['games_played']+=1
    except:
        tiles_played[moves_raw.split('\n')[2].split()[1]] = {'games_played':1}
    list_of_moves = moves_raw.split('\n')[3:]
    for index, move in enumerate(list_of_moves):
        data = move.split()
        try:
            data2 = list_of_moves[index+1].split()
            
        except:
            #last move
            break
        if data2:
            if data2[0].startswith('#'):
                data[2] = data[2].upper()
                move = data[2:4]
                score = data[4][1:]
                last_player=player
                player = data[0][1:-1]
                
                
                game_state = copy.deepcopy(game.state)
                if len(data)>5:
                    if int(score) > max_score:
                        max_score = int(score)
                        max_player = player
                        max_word = move[1]
                    response = move_input(game_state,move,player)
                    good=response[0]
                    for letter in response[1]:
                        try:
                            tiles_played[player][letter]+= 1
                        except:
                            try:
                                tiles_played[player][letter] = 1
                            except:
                                tiles_played[player] = {}
                                tiles_played[player][letter] = 1
                        
                    if good:
                        game.state = game_state
                
                    
        else:
            for letter in data[1][1:-1]:
                        try:
                            tiles_played[last_player][letter] += 1
                        except:
                            tiles_played[last_player][letter] = 1
 
    #split list of moves and pools
    if moves_raw.find('Game even')>-1:
        moves_raw =  moves_raw.split('Game even')[0]
    else:
        moves_raw = moves_raw.split('wins the game')[0]
    moves_raw = moves_raw.split('POOL')[1:]
    
    
    for item in moves_raw:
        data = item.split()
        move = data[data.index('pool')+1:]
        game.moves.append(move)
        pool = data[:data.index('letters')-1]
        game.racks.append(get_rack(game,pool))
        game_state = copy.deepcopy(game.state)
        if len(move[1])<4:
            response = move_input(game_state,move[1:3],move[0])
            good=response[0]
            # tiles_played = response[1]
            if good:
                game.state = game_state
def quackle_file(file):
    global game
    game = Game()
    
    f = open(file,'r')
    
    moves = f.read()
    f.close()
    move_list(game,moves)
    return phonies,bingos  
def reset_stats():
    global max_score,max_player,max_word
    bingos.clear()
    phonies.clear()
    max_score = 0
    max_word = ''
    max_player = ''
def check_files():
    

    games = [f'{n} {game}' for n,game in enumerate(os.listdir('./data/quackle/gamessent')) if game.endswith('.gcg')]
    return ', '.join(games)
def process_files():
    
   
    games = [game for game in os.listdir('./data/quackle/gamessent') if game.endswith('.gcg')]
    for gamefile in games:

        quackle_file(f'./data/quackle/gamessent/{gamefile}')
        

    f = open('bingos.json','w')
    f.write(json.dumps(player_bingos,indent=2))
    f.close()
    f = open('tiles_played.json','w')
    f.write(json.dumps(tiles_played,indent=2))
    f.close()
    f = open('phonies.json','w')
    max_stats = {"phonies":phonies, "max_score":max_score, "max_player":max_player, "max_word":max_word}
    f.write(json.dumps(max_stats,indent=2))
    f.close()
    total = 0
    for player in tiles_played:
        for tile in tiles_played[player]:
            total+=tiles_played[player][tile]
    
def get_rack(game,pool):
    rack = copy.deepcopy(game.tiles_not_on_board)
    for letter_count in pool:
        letter = letter_count[0]
        count = int(letter_count[2:])
        rack[letter]-=count
    rack_string = ''
    for letter in rack:
        rack_string += letter*rack[letter]
    return rack_string
def calc_stats():
    process_files()

    

    f = open('bingos.json','r')
    bingos = json.loads(f.read())
    f.close()
    f = open('tiles_played.json','r')
    tiles_played = json.loads(f.read())
    f.close()
    f=open('phonies.json','r')
    phonies = json.loads(f.read())
    f.close()

    def sort_func(player):
        return -1*len(bingos[player])
    sorted_bingos = [*bingos.keys()]
    sorted_bingos.sort(key=sort_func)
    file_to_send = ''
    for player in sorted_bingos:
        file_to_send += f'\n\n{player}: {len(bingos[player])}'
        print(f'\n{player}: {len(bingos[player])}')
        for bingo in bingos[player]:
            if not bingo.endswith('*'):
                alphagram = dic.TWL[bingo][4]
                num_anagrams = len(dic.alpha_dic[alphagram])
                file_to_send += f'\n{alphagram}({num_anagrams}) ||{bingo}||'
                print(f'{alphagram}({num_anagrams}) ||{bingo}||')
            else:
                file_to_send += f'\n{player}: {bingo}'
                print(f'{player}: {bingo}')
    most_Q = {"player":'',"number":0}
    most_J = {"player":'',"number":0}
    most_X = {"player":'',"number":0}
    most_Z = {"player":'',"number":0}
    most_blank = {"player":'',"number":0}
    most_S = {"player":'',"number":0}
    most_power = {"player":'',"number":0}
    most_U = {"player":'',"number":0}
    most_Q_per_game = {"player":'',"number":0}
    most_J_per_game = {"player":'',"number":0}
    most_X_per_game = {"player":'',"number":0}
    most_Z_per_game = {"player":'',"number":0}
    most_blank_per_game = {"player":'',"number":0}
    most_S_per_game = {"player":'',"number":0}
    most_power_per_game = {"player":'',"number":0}
    most_U_per_game = {"player":'',"number":0}
    for player in tiles_played:

        try:    
            if tiles_played[player]['Q'] > most_Q['number']:
                most_Q['number'] = tiles_played[player]['Q']
                most_Q['player'] = player
        except KeyError:
            tiles_played[player]['Q']=0
        try:
            if tiles_played[player]['Z'] > most_Z['number']:
                most_Z['number'] = tiles_played[player]['Z']
                most_Z['player'] = player
        except KeyError:
            tiles_played[player]['Z']=0
        try:
            if tiles_played[player]['J'] > most_J['number']:
                most_J['number'] = tiles_played[player]['J']
                most_J['player'] = player
        except KeyError:
            tiles_played[player]['J']=0
        try:
            if tiles_played[player]['X'] > most_X['number']:
                most_X['number'] = tiles_played[player]['X']
                most_X['player'] = player
        except KeyError:
            tiles_played[player]['X']=0
        try:
            if tiles_played[player]['S'] > most_S['number']:
                most_S['number'] = tiles_played[player]['S']
                most_S['player'] = player
        except KeyError:
            tiles_played[player]['S']=0
        try:
            if tiles_played[player]['?'] > most_blank['number']:
                most_blank['number'] = tiles_played[player]['?']
                most_blank['player'] = player
        except KeyError:
            tiles_played[player]['?']=0
        try:
            if tiles_played[player]['U'] > most_U['number']:
                most_U['number'] = tiles_played[player]['U']
                most_U['player'] = player
        except KeyError:
            tiles_played[player]['U']=0

        if tiles_played[player]['Q']+tiles_played[player]['Z']+tiles_played[player]['J']+tiles_played[player]['X']+tiles_played[player]['S']+tiles_played[player]['?'] > most_power['number']:
            most_power['number'] = tiles_played[player]['Q']+tiles_played[player]['Z']+tiles_played[player]['J']+tiles_played[player]['X']+tiles_played[player]['S']+tiles_played[player]['?']
            most_power['player'] = player

        try:    
            if tiles_played[player]['Q']/tiles_played[player]['games_played'] > most_Q_per_game['number']:
                most_Q_per_game['number'] = tiles_played[player]['Q']/tiles_played[player]['games_played']
                most_Q_per_game['player'] = player
        except KeyError:
            tiles_played[player]['Q']=0
        try:
            if tiles_played[player]['Z']/tiles_played[player]['games_played'] > most_Z_per_game['number']:
                most_Z_per_game['number'] = tiles_played[player]['Z']/tiles_played[player]['games_played']
                most_Z_per_game['player'] = player
        except KeyError:
            tiles_played[player]['Z']=0
        try:
            if tiles_played[player]['J']/tiles_played[player]['games_played'] > most_J_per_game['number']:
                most_J_per_game['number'] = tiles_played[player]['J']/tiles_played[player]['games_played']
                most_J_per_game['player'] = player
        except KeyError:
            tiles_played[player]['J']=0
        try:
            if tiles_played[player]['X']/tiles_played[player]['games_played'] > most_X_per_game['number']:
                most_X_per_game['number'] = tiles_played[player]['X']/tiles_played[player]['games_played']
                most_X_per_game['player'] = player
        except KeyError:
            tiles_played[player]['X']=0
        try:
            if tiles_played[player]['S']/tiles_played[player]['games_played'] > most_S_per_game['number']:
                most_S_per_game['number'] = tiles_played[player]['S']/tiles_played[player]['games_played']
                most_S_per_game['player'] = player
        except KeyError:
            tiles_played[player]['S']=0
        try:
            if tiles_played[player]['?']/tiles_played[player]['games_played'] > most_blank_per_game['number']:
                most_blank_per_game['number'] = tiles_played[player]['?']/tiles_played[player]['games_played']
                most_blank_per_game['player'] = player
        except KeyError:
            tiles_played[player]['?']=0
        try:
            if tiles_played[player]['U']/tiles_played[player]['games_played'] > most_U_per_game['number']:
                most_U_per_game['number'] = tiles_played[player]['U']/tiles_played[player]['games_played']
                most_U_per_game['player'] = player
        except KeyError:
            tiles_played[player]['U']=0

        if (tiles_played[player]['Q']+tiles_played[player]['Z']+tiles_played[player]['J']+tiles_played[player]['X']+tiles_played[player]['S']+tiles_played[player]['?'])/tiles_played[player]['games_played'] > most_power_per_game['number']:
            most_power_per_game['number'] = (tiles_played[player]['Q']+tiles_played[player]['Z']+tiles_played[player]['J']+tiles_played[player]['X']+tiles_played[player]['S']+tiles_played[player]['?'])/tiles_played[player]['games_played']
            most_power_per_game['player'] = player

    
    file_to_send += f'\n\nMost Qs: {most_Q["player"]} - {most_Q["number"]}'
    file_to_send += f'\nMost Js: {most_J["player"]} - {most_J["number"]}'
    file_to_send += f'\nMost Zs: {most_Z["player"]} - {most_Z["number"]}'
    file_to_send += f'\nMost Xs: {most_X["player"]} - {most_X["number"]}'
    file_to_send += f'\nMost Ss: {most_S["player"]} - {most_S["number"]}'
    file_to_send += f'\nMost blanks: {most_blank["player"]} - {most_blank["number"]}'
    file_to_send += f'\nMost power tiles: {most_power["player"]} - {most_power["number"]}'
    file_to_send += f'\nMost Us: {most_U["player"]} - {most_U["number"]}'
    least_Q = {"player":'',"number":1000}
    least_J = {"player":'',"number":1000}
    least_X = {"player":'',"number":1000}
    least_Z = {"player":'',"number":1000}
    least_blank = {"player":'',"number":1000}
    least_S = {"player":'',"number":1000}
    least_power = {"player":'',"number":1000}
    least_U = {"player":'',"number":1000}
    least_Q_per_game = {"player":'',"number":1000}
    least_J_per_game = {"player":'',"number":1000}
    least_X_per_game = {"player":'',"number":1000}
    least_Z_per_game = {"player":'',"number":1000}
    least_blank_per_game = {"player":'',"number":1000}
    least_S_per_game = {"player":'',"number":1000}
    least_power_per_game = {"player":'',"number":1000}
    least_U_per_game = {"player":'',"number":1000}
    for player in tiles_played:
        if tiles_played[player]['Q'] < least_Q['number']:
            least_Q['number'] = tiles_played[player]['Q']
            least_Q['player'] = player
        if tiles_played[player]['Z'] < least_Z['number']:
            least_Z['number'] = tiles_played[player]['Z']
            least_Z['player'] = player
        if tiles_played[player]['J'] < least_J['number']:
            least_J['number'] = tiles_played[player]['J']
            least_J['player'] = player
        if tiles_played[player]['X'] < least_X['number']:
            least_X['number'] = tiles_played[player]['X']
            least_X['player'] = player
        if tiles_played[player]['S'] < least_S['number']:
            least_S['number'] = tiles_played[player]['S']
            least_S['player'] = player
        if tiles_played[player]['?'] < least_blank['number']:
            least_blank['number'] = tiles_played[player]['?']
            least_blank['player'] = player
        if tiles_played[player]['U'] < least_U['number']:
            least_U['number'] = tiles_played[player]['U']
            least_U['player'] = player
        if tiles_played[player]['Q']+tiles_played[player]['Z']+tiles_played[player]['J']+tiles_played[player]['X']+tiles_played[player]['S']+tiles_played[player]['?'] < least_power['number']:
            least_power['number'] = tiles_played[player]['Q']+tiles_played[player]['Z']+tiles_played[player]['J']+tiles_played[player]['X']+tiles_played[player]['S']+tiles_played[player]['?']
            least_power['player'] = player
        try:    
            if tiles_played[player]['Q']/tiles_played[player]['games_played'] < least_Q_per_game['number']:
                least_Q_per_game['number'] = tiles_played[player]['Q']/tiles_played[player]['games_played']
                least_Q_per_game['player'] = player
        except KeyError:
            tiles_played[player]['Q']=0
        try:
            if tiles_played[player]['Z']/tiles_played[player]['games_played'] < least_Z_per_game['number']:
                least_Z_per_game['number'] = tiles_played[player]['Z']/tiles_played[player]['games_played']
                least_Z_per_game['player'] = player
        except KeyError:
            tiles_played[player]['Z']=0
        try:
            if tiles_played[player]['J']/tiles_played[player]['games_played'] < least_J_per_game['number']:
                least_J_per_game['number'] = tiles_played[player]['J']/tiles_played[player]['games_played']
                least_J_per_game['player'] = player
        except KeyError:
            tiles_played[player]['J']=0
        try:
            if tiles_played[player]['X']/tiles_played[player]['games_played'] < least_X_per_game['number']:
                least_X_per_game['number'] = tiles_played[player]['X']/tiles_played[player]['games_played']
                least_X_per_game['player'] = player
        except KeyError:
            tiles_played[player]['X']=0
        try:
            if tiles_played[player]['S']/tiles_played[player]['games_played'] < least_S_per_game['number']:
                least_S_per_game['number'] = tiles_played[player]['S']/tiles_played[player]['games_played']
                least_S_per_game['player'] = player
        except KeyError:
            tiles_played[player]['S']=0
        try:
            if tiles_played[player]['?']/tiles_played[player]['games_played'] < least_blank_per_game['number']:
                least_blank_per_game['number'] = tiles_played[player]['?']/tiles_played[player]['games_played']
                least_blank_per_game['player'] = player
        except KeyError:
            tiles_played[player]['?']=0
        try:
            if tiles_played[player]['U']/tiles_played[player]['games_played'] < least_U_per_game['number']:
                least_U_per_game['number'] = tiles_played[player]['U']/tiles_played[player]['games_played']
                least_U_per_game['player'] = player
        except KeyError:
            tiles_played[player]['U']=0

        if (tiles_played[player]['Q']+tiles_played[player]['Z']+tiles_played[player]['J']+tiles_played[player]['X']+tiles_played[player]['S']+tiles_played[player]['?'])/tiles_played[player]['games_played'] < least_power_per_game['number']:
            least_power_per_game['number'] = (tiles_played[player]['Q']+tiles_played[player]['Z']+tiles_played[player]['J']+tiles_played[player]['X']+tiles_played[player]['S']+tiles_played[player]['?'])/tiles_played[player]['games_played']
            least_power_per_game['player'] = player

    print(f'\nFewest Qs: {least_Q["player"]} - {least_Q["number"]}')
    print(f'Fewest Js: {least_J["player"]} - {least_J["number"]}')
    print(f'Fewest Zs: {least_Z["player"]} - {least_Z["number"]}')
    print(f'Fewest Xs: {least_X["player"]} - {least_X["number"]}')
    print(f'Fewest Ss: {least_S["player"]} - {least_S["number"]}')
    print(f'Fewest blanks: {least_blank["player"]} - {least_blank["number"]}')
    print(f'Fewest power tiles: {least_power["player"]} - {least_power["number"]}')
    print(f'Fewest Us: {least_U["player"]} - {least_U["number"]}')
    file_to_send += f'\n\nFewest Qs: {least_Q["player"]} - {least_Q["number"]}'
    file_to_send += f'\nFewest Js: {least_J["player"]} - {least_J["number"]}'
    file_to_send += f'\nFewest Zs: {least_Z["player"]} - {least_Z["number"]}'
    file_to_send += f'\nFewest Xs: {least_X["player"]} - {least_X["number"]}'
    file_to_send += f'\nFewest Ss: {least_S["player"]} - {least_S["number"]}'
    file_to_send += f'\nFewest blanks: {least_blank["player"]} - {least_blank["number"]}'
    file_to_send += f'\nFewest power tiles: {least_power["player"]} - {least_power["number"]}'
    file_to_send += f'\nFewest Us: {least_U["player"]} - {least_U["number"]}'
    print('\nPhonies:')
    file_to_send += '\n\nPhonies:'
    for phony in phonies:
        if phony == 'phonies':
            for word in sorted(phonies[phony]):
                print(word)
                file_to_send += f'\n{word}'
        else:
            print(f'\n{phony}: {phonies[phony]}')
            file_to_send += f'\n{phony}: {phonies[phony]}'
    print(f'\nMost Qs per game: {most_Q_per_game["player"]} - {round(most_Q_per_game["number"],2)}')
    print(f'Most Js per game: {most_J_per_game["player"]} - {round(most_J_per_game["number"],2)}')
    print(f'Most Zs per game: {most_Z_per_game["player"]} - {round(most_Z_per_game["number"],2)}')
    print(f'Most Xs per game: {most_X_per_game["player"]} - {round(most_X_per_game["number"],2)}')
    print(f'Most Ss per game: {most_S_per_game["player"]} - {round(most_S_per_game["number"],2)}')
    print(f'Most blanks per game: {most_blank_per_game["player"]} - {round(most_blank_per_game["number"],2)}')
    print(f'Most power tiles per game: {most_power_per_game["player"]} - {round(most_power_per_game["number"],2)}')
    print(f'Most Us per game: {most_U_per_game["player"]} - {round(most_U_per_game["number"],2)}')
    print(f'\nFewest Qs per game: {least_Q_per_game["player"]} - {round(least_Q_per_game["number"],2)}')
    print(f'Fewest Js per game: {least_J_per_game["player"]} - {round(least_J_per_game["number"],2)}')
    print(f'Fewest Zs per game: {least_Z_per_game["player"]} - {round(least_Z_per_game["number"],2)}')
    print(f'Fewest Xs per game: {least_X_per_game["player"]} - {round(least_X_per_game["number"],2)}')
    print(f'Fewest Ss per game: {least_S_per_game["player"]} - {round(least_S_per_game["number"],2)}')
    print(f'Fewest blanks per game: {least_blank_per_game["player"]} - {round(least_blank_per_game["number"],2)}')
    print(f'Fewest power tiles per game: {least_power_per_game["player"]} - {round(least_power_per_game["number"],2)}')
    print(f'Fewest Us per game: {least_U_per_game["player"]} - {round(least_U_per_game["number"],2)}')
    bingos_per_game = {}
    for player in sorted_bingos:
        bingos_per_game[player] = len(bingos[player])/tiles_played[player]["games_played"]


    def sort_func2(player):
        return bingos_per_game[player]
    sorted_bingos_per_game = [*bingos.keys()]
    sorted_bingos_per_game.sort(key=sort_func2)
    for player in sorted_bingos_per_game:
        print(f'{player}: {round(bingos_per_game[player],2)}')
    return file_to_send
def write_quackle(game,csw=False,player2_score=0,player1_score=0,round_number=1):
    global max_score, max_word, max_player
    n = round_number
    print(game)
    player1_name = game.moves[0][0][:-1].upper()
    player2_name = game.moves[1][0][:-1].upper()
    total = {player1_name.upper(): 0, player2_name.upper(): 0}
    p1f,p2f = sorted([player1_name,player2_name])
    filename = f'{p1f.lower()}_vs_{p2f.lower()}'
    f = open('data/quackle/timestamps.txt','r')
    times = f.read().split('\n')[1:len(game.moves)+1]
    f.close()
    while True:
        try:
            f = open(f'data/quackle/gamessent/{filename}{n}.gcg', 'r')
            n+=1
        except:
            f = open(f'data/quackle/games/{filename}{n}.gcg', 'w')
            challenge_total = {player1_name.upper(): 0, player2_name.upper(): 0}
            f.write(f'#character-encoding UTF-8\n')
            f.write(f'#player1 {player1_name.upper()} {player1_name.upper()}\n')
            f.write(f'#player2 {player2_name.upper()} {player2_name.upper()}\n')
            prev_used_time = 0
            next_min,next_sec = times[0].split(',')[1].split(':')
            next_time = int(next_min)*60 + int(next_sec)
            for x, parts in enumerate(game.moves):
                time = times[x].split(',')
                p1min, p1sec = time[x%2].split(':')
                p1time = int(p1min)*60 + int(p1sec)
                
                time_used = next_time - p1time
                next_min,next_sec = time[1-x%2].split(':')
                next_time = int(next_min)*60 + int(next_sec)
                if x+1== len(game.moves):  # last move of game, countback
                    if name == player1_name.upper():
                        score = (player1_score - player2_score) - (
                            total[player1_name.upper()] - total[player2_name.upper()])
                    else:
                        score = (player2_score - player1_score) - (
                            total[player2_name.upper()] - total[player1_name.upper()])
                    cmove = f'({game.racks[x].upper()})'
                    total[name] += score
                    f.write(f'>{name}: {cmove} +{score} {total[name]}\n')
                    break
                name = parts[0][0:-1].upper()
                if parts[1] == 'CHANGE':  # an exchange
                    cmove = f'-{game.racks[x][0:int(parts[2])].lower()}'
                    score = 0

                elif len(parts) == 4 and parts[1].lower() != 'wins':  # simple move
                    parts[1] = swap_orientation(parts[1])
                    cmove = ' '.join(parts[1:3])
                    score = parts[3]
                    total[name] += int(score)
                elif len(parts) == 2 and parts[1].upper() == 'PASS':  # simple pass
                    cmove = '-'
                    score = 0
                elif len(parts) == 5 and parts[
                    4].lower() == '(challenged)':  # play is challenged unsuccessfully

                    parts[1] = swap_orientation(parts[1])
                    cmove = ' '.join(parts[1:3])
                    score = parts[3]
                    total[name] += int(score)
                    if csw:
                        f.write(f'>{name}: {game.racks[x]} {cmove.swapcase()} +{score} {total[name]}\n')
                                        
                        f.write(f'>{name}: {game.racks[x+1]} (challenge) +5 {total[name] + 5}\n')
                                        
                        total[name] += 5
                        challenge_total[
                            name] -= 5  # fix because ISC uses -5 to the challenger, Quackle uses +5 to the challengee
                        continue

                elif len(parts) == 5 and parts[1].lower() == 'pass':  # play is challenged successfully
                    parts[2] = swap_orientation(parts[2][1:])
                    cmove = ' '.join(parts[2:4])
                    score = parts[4][:-1]

                    f.write(
                        f'>{name}: {game.racks[x]} {cmove.swapcase()} +{score} {total[name] + int(score)}\n')
                                    
                    f.write(f'>{name}: {game.racks[x]} -- -{score} {total[name]}\n')
                    
                    f.write(f'#note Time used on opponent\'s clock: {prev_used_time} seconds, ')
                    f.write(f'Time used on own clock: {time_used} seconds, ')
                    f.write(f'Total time used: {prev_used_time + time_used} seconds\n')
                    prev_used_time = time_used
                    continue

                f.write(f'>{name}: {game.racks[x]} {cmove.swapcase()} +{score} {total[name]}\n')
                f.write(f'#note Time used on opponent\'s clock: {prev_used_time} seconds, ')
                f.write(f'Time used on own clock: {time_used} seconds, ')
                f.write(f'Total time used: {prev_used_time + time_used} seconds\n')
                prev_used_time = time_used
                if int(score) > max_score:
                    max_score = int(score)
                    max_word = cmove.upper()
                    max_player = name
            f.close()
            break
def swap_orientation(move):
    decode = {'A': '1', 'B': '2', 'C': '3', 'D': '4', 'E': '5',
             'F': '6', 'G': '7', 'H': '8', 'I': '9', 'J': '10',
            'K': '11', 'L': '12', 'M': '13', 'N': '14', 'O': '15',
           '1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E',
          '6': 'F', '7': 'G', '8': 'H', '9': 'I', '10': 'J',
         '11': 'K', '12': 'L', '13': 'M', '14': 'N', '15': 'O'}
    
    if move[0].isalpha():
        output = decode[move[0]] + decode[move[1:]]
    else:
        output = decode[move[:-1]] + decode[move[-1]]

    return output

def quackle(p1s,p2s,round_number):
    global game
    game = Game()

    f = open('data/quackle/moves.txt','r')
    
    moves = f.read()
    f.close()
    
    move_list(game,moves)
    
    write_quackle(game,False,p2s,p1s,round_number)
    return phonies,bingos

def reset_stats():
    global max_score,max_player,max_word
    bingos.clear()
    phonies.clear()
    max_score = 0
    max_word = ''
    max_player = ''

def save_stats():
    import json
    f = open('data/tourney/bingos.dat','w')
    f.write(json.dumps(bingos))
    f.close()
    f = open('data/tourney/phonies.dat','w')
    f.write(json.dumps(phonies))
    f.close()
    f=open('data/tourney/stats.dat','w')
    f.write(max_score)
    f.write(max_word)
    f.write(max_player)
    f.close()

def load_stats():
    global bingos,phonies,max_player,max_score,max_word
    
    f = open('data/tourney/bingos.dat','r')
    bingos=json.loads(f.read())
    f.close()
    f = open('data/tourney/phonies.dat','r')
    phonies=json.loads(f.read())
    f.close()
    f=open('data/tourney/stats.dat','r')
    f.readline(max_score)
    f.readline(max_word)
    f.readline(max_player)
    f.close()

