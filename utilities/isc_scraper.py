import time
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime
from utilities.scraper_elements import *
import utilities.gamesim as gs
options = Options()

if __name__ != '__main__':
    options.add_argument("--headless")  # so the browser is not visible


debug = False


driver = None

def get_games(playerlist, penalty=True, quackle=False, start_pos=1,round_number=1):

    
    global driver
    driver = webdriver.Chrome(options=options)
    results = []
    
    driver.get('http://www.isc.ro')
    choose_english = get(CE) 
    choose_english.click()

    time.sleep(1)
    login_username = get(LU)
    login_username.send_keys('Scrabble69')
    login_password = get(LP)
    login_password.send_keys('1U0GHZH4J2')
    connect_button = get(CB)
    connect_button.click()
    single = False
    for pair in playerlist:
        command_textbox = get(CT)
        if len(pair) == 2:
            p1, p2 = pair
        else:
            p1 = pair[0]
            p2 = ''
            single = True
        command_textbox.send_keys(f'hi {p1}\n')
        print(f'Looking for {p1.upper(), p2.upper()}')
        #try:
        for n in range(start_pos, 11):
            
            selected_game = get(SG(n))
            try:
                selected_game_text = selected_game.text.split(')')[1]
                selected_game_text = selected_game_text.split()
            except:
                selected_game = get(SG(n))
                selected_game_text = selected_game.text.split(')')[1]
                selected_game_text = selected_game_text.split()
                
            player1 = selected_game_text[1].upper()
            player2 = selected_game_text[4].upper()

            print(player1,player2)
            if {player1, player2} == {p1.upper(), p2.upper()} or single:
                print(f'Found {player1,player2}')
                time.sleep(2)
                selected_game = get(VG(n))
                selected_game.click()
                    
                print('close')
                close = get(CL)
                close.click()

                time.sleep(1)
                    
                player1_name_score_text = get(P1N)
                player2_name_score_text = get(P2N)
                player1_clock = get(P1C)
                player2_clock = get(P2C)
                player1_text = player1_name_score_text.text
                player2_text = player2_name_score_text.text

                player1_penalty = 10 * (10 - int(player1_clock.text.split(':')[0])) if 10 - int(
                    player1_clock.text.split(':')[0]) > 0 and penalty else 0
                player2_penalty = 10 * (10 - int(player2_clock.text.split(':')[0])) if 10 - int(
                    player2_clock.text.split(':')[0]) > 0 and penalty else 0

                player1_name = player1_text.split()[1]
                player1_score = int(player1_text.split()[2])

                player2_name = player2_text.split()[1]
                player2_score = int(player2_text.split()[2])

                message = f'{player1_name} {player1_score - player1_penalty} {player2_name} {player2_score - player2_penalty}'

                results=[f'{message}']
                if quackle:
                            
                    start_of_game = get(ST)
                    start_of_game.click()
                    timestamps = [[player1_clock.text, player2_clock.text]]    
                    for _ in range(40):
                        command_textbox.send_keys(f'pool\n')
                        next_move = get(NM)
                        next_move.click()
                        timestamps.append([player1_clock.text, player2_clock.text])
                    import random

                            
                    chat_window = get(CW)
                    # csw = False
                    # if chat_window.text.find('CSW') > -1:
                    #     csw = True
                    if chat_window.text.find('Game even') > -1:
                        start_move = chat_window.text.find('Game even') + 15
                    else:
                        start_move = chat_window.text.find('wins the game') + 15
                    if chat_window.text.find('forfeit on') > -1:
                        start_move = chat_window.text.find('time)', start_move) + 7

                    moves = chat_window.text[start_move:].split('\n')
                    m = open('data/quackle/moves.txt','w')
                    m.write('\n'.join(move for move in moves))
                    m.close()
                    m = open('data/quackle/timestamps.txt','w')
                    m.write('\n'.join(f'{timestamp[0]},{timestamp[1]}' for timestamp in timestamps))
                    m.close()
                    command_textbox.send_keys(f'clear\n')
        
                    # phonies,bingos=gs.quackle(player1_score,player2_score,round_number)
                    gs.quackle(player1_score,player2_score,round_number)

                break
            else:
                results.append(('error', f'{p1} vs {p2} not found, try again'))
        #except Exception as e:
        #    print(e)
        #    results.append(f'{playerlist.index(pair)}')
        #    break
    if debug:
        time.sleep(1)
    driver.quit()
    driver.stop_client()
    return results
def get(xpath):
    for _ in range(3):
        try:
            return driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            time.sleep(2)

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


