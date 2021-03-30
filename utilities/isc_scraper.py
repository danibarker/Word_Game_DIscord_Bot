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


def get_games(playerlist, penalty=True, quackle=False, start_pos=1, round_number=1):
    '''
    connects to ISC with a webscraper
    finds and clicks specific elements on the page
    to get a text summary of the moves, scores, and
    timers

    returns an array of dicts with a success boolean,
    and if success is true, a formatted result to use in parse_result function

    eg. [{"success":True, message:"danib 345 runesman 345"},...]
    '''
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

    for pair in playerlist:
        command_textbox = get(CT)
        p1, p2 = pair
        command_textbox.send_keys(f'hi {p1}\n')
        game_index = None
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

            if {player1, player2} != {p1.upper(), p2.upper()}:
                continue
            game_index = n
            break

        if not game_index:
            results.append(
                {"success": False, "message": f'{p1} vs {p2} not found'})
            continue

        selected_game_button = get(VG(game_index))
        selected_game_button.click()

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

        results.append({"success": True, "message": message})

        if quackle:

            write_moves_list_file(
                player1_clock, player2_clock, command_textbox)
            gs.write_quackle_file(player1_score, player2_score, round_number)

    driver.quit()
    driver.stop_client()

    return results


def write_moves_list_file(player1_clock, player2_clock, command_textbox):
    '''
    cycles through moves in the game to make the move info display
    on the chat/info window of ISC,
    grabs that move info and the timestamps for each move
    writes the timestamps and moves to files
    '''
    start_of_game = get(ST)
    start_of_game.click()
    timestamps = [[player1_clock.text, player2_clock.text]]
    for _ in range(40):
        command_textbox.send_keys(f'pool\n')
        next_move = get(NM)
        next_move.click()
        timestamps.append([player1_clock.text, player2_clock.text])

    chat_window = get(CW)
    if chat_window.text.find('Game even') > -1:
        start_move = chat_window.text.find('Game even') + 15
    else:
        start_move = chat_window.text.find('wins the game') + 15
    if chat_window.text.find('forfeit on') > -1:
        start_move = chat_window.text.find('time)', start_move) + 7

    moves = chat_window.text[start_move:].split('\n')

    m = open('data/quackle/moves.txt', 'w')
    m.write('\n'.join(move for move in moves))
    m.close()

    m = open('data/quackle/timestamps.txt', 'w')
    m.write(
        '\n'.join(f'{timestamp[0]},{timestamp[1]}' for timestamp in timestamps))
    m.close()

    command_textbox.send_keys(f'clear\n')


def get(xpath):
    '''
    finds an element with the full xpath given
    '''
    for _ in range(3):
        try:
            return driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            time.sleep(2)
