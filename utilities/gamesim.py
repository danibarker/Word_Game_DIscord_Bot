'''
-------------------------------------------------------------
| This simulates a game  of scrabble given a list of moves. |
| Currently just used in order to calculate what players    |
| racks are on any given move in order to generate an       |
| accurate gcg file                                         |
-------------------------------------------------------------
'''
import os
import copy
import modules.club as club
import modules.dictionary as dic
import json
from utilities.gameclass import Game

def move(board, row, column, word, orientation):

    global plain_word
    tiles_played = []
    row = row-1
    column = column-1

    if orientation == 1:

        for n, y in enumerate(range(row, row+len(word))):
            if board[column][y] == '.' or board[column][y] == word[n]:
                if not board[column][y] == word[n]:
                    tiles_played.append(word[n])
                board[column][y] = word[n]

            else:
                return False, None
        for tile in tiles_played:
            game.tiles_not_on_board[tile] -= 1

        return True, tiles_played

    if orientation == 0:

        for n, x in enumerate(range(column, column+len(word))):
            if board[x][row] == '.' or board[x][row] == word[n]:
                if not board[x][row] == word[n]:
                    tiles_played.append(word[n])
                board[x][row] = word[n]
            else:

                return False, None
        for tile in tiles_played:
            game.tiles_not_on_board[tile] -= 1
        return True, tiles_played


def move_input(board, play):
    global plain_word
    row_conv = '.ABCDEFGHIJKLMNO'  # to convert letter row to number
    word = play[1]
    plain_word = word.upper()
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':

        word = word.replace(letter, '?')  # convert blanks to ?
    word = word.upper()

    position = play[0]
    if position[0].isalpha():
        row = row_conv.index(position[0])
        column = int(position[1:])
        orientation = 0
    else:
        column = int(position[:-1])
        row = row_conv.index(position[-1:])
        orientation = 1
    return move(board, row, column, word, orientation)


def move_list(game, moves_raw):
    # split list of moves and pools
    if moves_raw.find('Game even') > -1:
        moves_raw = moves_raw.split('Game even')[0]
    else:
        moves_raw = moves_raw.split('wins the game')[0]
    moves_raw = moves_raw.split('POOL')[1:]

    for item in moves_raw:
        data = item.split()
        move = data[data.index('pool')+1:]
        game.moves.append(move)
        pool = data[:data.index('letters')-1]
        game.racks.append(get_rack(game, pool))
        game_state = copy.deepcopy(game.state)
        if len(move[1]) < 4:
            response = move_input(game_state, move[1:3])
            good = response[0]
            # tiles_played = response[1]
            if good:
                game.state = game_state


def get_rack(game, pool):
    rack = copy.deepcopy(game.tiles_not_on_board)
    for letter_count in pool:
        letter = letter_count[0]
        count = int(letter_count[2:])
        rack[letter] -= count
    rack_string = ''
    for letter in rack:
        rack_string += letter*rack[letter]
    return rack_string


def write_quackle(game, csw=False, player2_score=0, player1_score=0, round_number=1):
    
    n = round_number
    print(game)
    player1_name = game.moves[0][0][:-1].upper()
    player2_name = game.moves[1][0][:-1].upper()
    total = {player1_name.upper(): 0, player2_name.upper(): 0}
    p1f, p2f = sorted([player1_name, player2_name])
    filename = f'{p1f.lower()}_vs_{p2f.lower()}'
    f = open('data/quackle/timestamps.txt', 'r')
    times = f.read().split('\n')[1:len(game.moves)+1]
    f.close()
    while True:
        try:
            f = open(f'data/quackle/gamessent/{filename}{n}.gcg', 'r')
            n += 1
        except:
            f = open(f'data/quackle/games/{filename}{n}.gcg', 'w')
            challenge_total = {
                player1_name.upper(): 0, player2_name.upper(): 0}
            f.write(f'#character-encoding UTF-8\n')
            f.write(
                f'#player1 {player1_name.upper()} {player1_name.upper()}\n')
            f.write(
                f'#player2 {player2_name.upper()} {player2_name.upper()}\n')
            prev_used_time = 0
            next_min, next_sec = times[0].split(',')[1].split(':')
            next_time = int(next_min)*60 + int(next_sec)
            for x, parts in enumerate(game.moves):
                time = times[x].split(',')
                p1min, p1sec = time[x % 2].split(':')
                p1time = int(p1min)*60 + int(p1sec)

                time_used = next_time - p1time
                next_min, next_sec = time[1-x % 2].split(':')
                next_time = int(next_min)*60 + int(next_sec)
                if x+1 == len(game.moves):  # last move of game, countback
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

                # simple move
                elif len(parts) == 4 and parts[1].lower() != 'wins':
                    parts[1] = swap_orientation(parts[1])
                    cmove = ' '.join(parts[1:3])
                    score = parts[3]
                    total[name] += int(score)
                # simple pass
                elif len(parts) == 2 and parts[1].upper() == 'PASS':
                    cmove = '-'
                    score = 0
                elif len(parts) == 5 and parts[
                        4].lower() == '(challenged)':  # play is challenged unsuccessfully

                    parts[1] = swap_orientation(parts[1])
                    cmove = ' '.join(parts[1:3])
                    score = parts[3]
                    total[name] += int(score)
                    if csw:
                        f.write(
                            f'>{name}: {game.racks[x]} {cmove.swapcase()} +{score} {total[name]}\n')

                        f.write(
                            f'>{name}: {game.racks[x+1]} (challenge) +5 {total[name] + 5}\n')

                        total[name] += 5
                        challenge_total[
                            name] -= 5  # fix because ISC uses -5 to the challenger, Quackle uses +5 to the challengee
                        continue

                # play is challenged successfully
                elif len(parts) == 5 and parts[1].lower() == 'pass':
                    parts[2] = swap_orientation(parts[2][1:])
                    cmove = ' '.join(parts[2:4])
                    score = parts[4][:-1]

                    f.write(
                        f'>{name}: {game.racks[x]} {cmove.swapcase()} +{score} {total[name] + int(score)}\n')

                    f.write(
                        f'>{name}: {game.racks[x]} -- -{score} {total[name]}\n')

                    f.write(
                        f'#note Time used on opponent\'s clock: {prev_used_time} seconds, ')
                    f.write(f'Time used on own clock: {time_used} seconds, ')
                    f.write(
                        f'Total time used: {prev_used_time + time_used} seconds\n')
                    prev_used_time = time_used
                    continue

                f.write(
                    f'>{name}: {game.racks[x]} {cmove.swapcase()} +{score} {total[name]}\n')
                f.write(
                    f'#note Time used on opponent\'s clock: {prev_used_time} seconds, ')
                f.write(f'Time used on own clock: {time_used} seconds, ')
                f.write(
                    f'Total time used: {prev_used_time + time_used} seconds\n')
                prev_used_time = time_used
                
            f.close()
            break


def swap_orientation(move):
    '''
    ISC has their columns and rows transposed from Quackle's
    this swaps them
    '''

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


def write_quackle_file(p1s, p2s, round_number):

    global game
    game = Game()

    f = open('data/quackle/moves.txt', 'r')

    moves = f.read()
    f.close()

    move_list(game, moves)

    write_quackle(game, False, p2s, p1s, round_number)

