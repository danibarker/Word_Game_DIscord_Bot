import re
import random
import difflib
import json
TWL = {}
CSW = {}
alpha_dic = {}
NOTES = {}
cache = ['...'] * 5000
cache_count = 1
alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def related(word, lexicon=TWL):
    my_result = []
 
    for w in lexicon:
        x = lexicon[w][0].upper()
        if re.search("[^a-zA-Z]" + word + "[^a-zA-Z]", x) \
                or re.search("[^a-zA-Z]" + word + "S[^a-zA-Z]", x) \
                or re.search("^" + word + "[^a-zA-Z]", x):
            my_result.append(w)

    num_results = len(my_result)
    msg = ''
    for p, _ in enumerate(my_result):
        if p < 50:
            msg += my_result[p] + "   "
        elif p > 49:
            cache[p // 50] += my_result[p] + "   "
    return num_results, msg


def starts_with(word, lexicon=TWL):
    my_result = []

    for w in lexicon:
        if re.search("^" + word.upper(), w):
            my_result.append(w)
    num_results = len(my_result)
    msg = ''
    for p, _ in enumerate(my_result):
        if p < 50:
            msg += my_result[p] + "   "
        elif p > 49:
            cache[p // 50] += my_result[p] + "   "
    return num_results, msg


def contains(word, lexicon=TWL):
    global cache_count
    global cache
    word = word.replace('?', '.').upper()
    my_result = []
  
    for w in lexicon:
        if re.search(word, w):
            my_result.append(w)
    num_results = len(my_result)
    msg = ''
    for p, _ in enumerate(my_result):
        if p < 50:
            msg += my_result[p] + "   "
        elif p > 49:
            cache_count = 1
            cache[p // 50] += my_result[p] + "   "
    return num_results, msg


def hidden(word, length, lexicon=TWL):
    phrase = word.upper().replace(" ", "")
    
    msg = ''
    for x in range(0, len(phrase) - length + 1):
        if phrase[x:x + length] in lexicon:
            msg = msg + phrase[x:x + length] + " "
    if not msg:
        msg = 'No hidden words'
    return msg


def pattern(word, lexicon=TWL):
    global cache_count
    global cache
    word = ('^' + word + '$').upper()
    my_result = []

    for w in lexicon:
        if re.search(word, w):
            my_result.append(w)
    num_results = len(my_result)
    msg = ''
    for p, _ in enumerate(my_result):
        if p < 50:
            msg += my_result[p] + "   "
        elif p > 49:
            cache_count = 1
            cache[p // 50] += my_result[p] + "   "
    return num_results, msg


def ends_with(word, lexicon=TWL):
    global cache_count
    global cache
    word = word.replace('?', '.').upper()
    my_result = []

    for w in lexicon:
        if re.search(word + "$", w):
            my_result.append(w)

    num_results = len(my_result)
    msg = ''
    for p, _ in enumerate(my_result):
        if p < 50:
            msg += my_result[p] + "   "
        elif p > 49:
            cache_count = 1
            cache[p // 50] += my_result[p] + "   "
    return num_results, msg


def define(word, asker = None, lexicon=TWL):
    guess = ''
    my_result = ''
    word = word.upper()

    try:
        my_result = lexicon[word][0]
    except KeyError:
        guess = difflib.get_close_matches(word, lexicon.keys(), 1, .1)[0]
        my_result = lexicon[guess][0]
    if guess:
        msg = word + " not found, did you mean \n" + guess.upper() + " - " + my_result
    else:
        msg = word.upper() + " - " + my_result

    try:
        msg = msg + "\nNotes: " + NOTES[asker][word]
    except KeyError:
        pass
    return msg


def info(word, asker=None, lexicon=TWL):
    word = word.upper()
    my_result = ''
    msg = ""

    try:
        my_result = lexicon[word]
    except KeyError:
        msg = "No such word"
    counter = -1
    for x in my_result:
        counter = counter + 1
        if counter == 0:
            msg = word + " - "
            counter += 1
        if counter == 1:
            msg = msg + x + "\n\n"
        if counter == 4:
            msg = msg + "Probability: " + str(x) + "\n\n"
        if counter == 5:
            msg = msg + "Alphagram: " + x
    msg = msg + "\n\nInserts: "


    inserts = [x for x in set(insertb(word, lexicon))]
    inserts.sort()
    for x in inserts:
        msg = msg + x + " "
    msg = msg + "\n\nSwaps: "


    swaps = [x for x in set(swapb(word, lexicon))]
    swaps.sort()
    for x in swaps:
        msg = msg + x + " "
    msg = msg + "\n\nDrops: "


    drops = [x for x in set(drop(word, lexicon))]
    drops.sort()
    for x in drops:
        msg = msg + x + " "
    msg = msg + "\n\nAnagrams: "


    anag = [x for x in set(anagram(word, lexicon))]
    anag.sort()
    for x in anag:
        msg = msg + x + " "
    try:
        msg = msg + "\n\nNotes: " + NOTES[asker][word]
    except KeyError:
        pass
    return msg


def random_word(lexicon=TWL):
    msg = ''
    
    my_result = random.choice(list(lexicon))
    msg = my_result + " - " + lexicon[my_result][0]

    return msg


def anagram_1(word, lexicon=TWL):
    global cache_count
    my_result = ''

    my_result = anagram(word.upper(), lexicon)
    
    num_results = len(my_result)
    msg = ''
    for p, _x in enumerate(my_result):
        if p < 50:
            msg += my_result[p] + "   "
        elif p > 49:
            cache_count = 0
            cache[p // 50] += my_result[p] + "   "
    return num_results, msg


def judge(words, lexicon=TWL):
    judged = True
    words = words.upper().split()

 
    for x in words:
        try:
            _temp = lexicon[x]
        except KeyError:
            judged = False

    if judged:
        msg = 'Acceptable'
    else:
        msg = 'Unacceptable'
    return msg


def next_results():
    global cache
    global cache_count
    msg = cache[cache_count]
    cache_count = cache_count + 1
    return msg


def add_note(word, note, asker):
    try:
        NOTES[asker][word] = note
    except KeyError:
        NOTES[asker] = {}
        NOTES[asker][word] = note
    save_notes()
    msg = "Note saved in " + word.upper()
    return msg


def get_notes(asker, query):
    found = False
    if query:
        try:
            msg = asker + "\'s notes:"
            for x in sorted(NOTES[asker].keys()):
                if NOTES[asker][x].upper().find(query.upper()) > -1:
                    msg += "\n" + x + " - " + NOTES[asker][x]
                    found = True

            if not found:
                msg = 'No notes'
        except KeyError:
            msg = "No notes"

    else:
        try:
            msg = asker + "\'s notes:"
            for x in sorted(NOTES[asker].keys()):
                msg += "\n" + x + " - " + NOTES[asker][x]
        except KeyError:
            msg = "No notes"
    return msg



def drop(s, lexicon=TWL):
    # RETURNS LIST OF STRINGS WITH ONE LETTER DROPPED
    result = []
    for x in range(0, len(s)):
        front = s[0:x]
        back = s[x + 1:]
        if front+back in lexicon:
            result.append(front + back)
    return result


def anagram(s, lexicon=TWL):
    my_result = []
    word_length = len(s)
    num_blanks = list(s).count('?')
    s = s.replace('?', '').upper()
    word2 = sorted(s.replace('?', ''))
    word3 = ''
    for _ in range(num_blanks):
        word3 = word3 + '.?'
    for x in word2:
        word3 = word3 + x
        for _ in range(num_blanks):
            word3 = word3 + '.?'
    expression = '^' + ''.join(word3) + '$'
    
    for x in lexicon:
        if re.search(expression, lexicon[x][4]) and len(x) == word_length:
            my_result.append(x)

    return my_result


def middle_hooks(s, lexicon=TWL):
    # FINDS LETTERS THAT CAN BE ADDED TO THE MIDDLE OF A WORD
    result = []
    
    for x in range(1, len(s)):
        word1 = s[0:x] + '.' + s[x:]
       
        for w in lexicon:
            if re.search('^' + word1.upper() + '$', w):
                result.append(w)
    return result

def insert(s,lexicon=TWL):
    result = []
    s=s.upper()
    for x in range(0, len(s)+1):
        for letter in alpha:
            word1 = s[0:x] + letter + s[x:]
            
            if word1 in lexicon:
                result.append(word1)
                
    return result
def insertb(s,lexicon=TWL):
    result = []
    s=s.upper()
    for x in range(0, len(s)+1):
        for letter in alpha:
            word1 = s[0:x] + letter + s[x:]
            
            if word1 in lexicon:
                result.append(f'{s[0:x]}**{letter}**{s[x:]}')
                
    return result
def swap(s, lexicon=TWL):
    result = []
    for x in range(0, len(s)):
        front = s[0:x]
        back = s[x + 1:]
        for letter in alpha:
            if front+letter+back in lexicon and not front+letter+back == s:
                result.append(f'{front}{letter}{back}')
    return set(result)
def swapb(s, lexicon=TWL):
    result = []
    for x in range(0, len(s)):
        front = s[0:x]
        back = s[x + 1:]
        for letter in alpha:
            if front+letter+back in lexicon and not front+letter+back == s:
                result.append(f'{front}**{letter}**{back}')
    return result

def crypto(word, lexicon=TWL):
    word = word.upper()
    newword = []
    groups = []
    for n,letter in enumerate(word):
        if letter in groups:

            newword.append(r'\ '[0]+f'{groups.index(letter)+1}')
        else:
            add = r'\ '[0]+r'|\ '[:-1].join(f'{n+1}' for n in range(len(groups)))
            if len(newword)>0:
                newword.append(f'(?!{add})')
            newword.append(f'([^{word[n]}])')
            
            groups.append(letter)
    print(''.join(newword))
    return pattern(f'{"".join(newword)}',lexicon)
def issubanagram(word,rack):
    
    return (0 not in [c in word for c in rack]) and (0 not in [0 for letter in [word.count(l)-rack.count(l) for l in word] if letter<0])

def subanagram(string,lexicon=TWL):
    string = string.upper()
    results = []
    msg = ''
    for word in (w for w in alpha_dic if len(w)<=len(string)):
        if issubanagram(string,word):
            for word in alpha_dic[word]:
                results.append(word)
    results = list(set(results))
    results.sort()
    for p, _ in enumerate(results):
        if p < 50:
            msg += results[p] + "   "
        elif p > 49:
            cache[p // 50] += results[p] + "   "
    return len(results),msg

def save_notes():
    # SAVES NOTES DICT TO FILE
    f = open('data/notes.dat', 'w')
    for x in NOTES:
        f.write(x + "	")
        for y in NOTES[x]:
            f.write(y)
            f.write('@')
            f.write(NOTES[x][y])
            f.write('$')
        f.write('\n')
    f.close()


def open_files():
    global alpha_dic
    f = open('data/notes.dat', 'r')
    line = f.readline().strip("\n").split('	', 1)
    while line != ['']:
        user = line[0]
        notes = line[1].split('$')
        NOTES[user] = {}
        for x in notes:
            temp = x.split('@')
            if len(temp) > 1:
                NOTES[user][temp[0]] = temp[1]
        line = f.readline().strip("\n").split('	', 1)
    f.close()
    
    
    f = open('data/lexica/twl_alpha.json', 'r')
    alpha_dic = json.loads(f.read())
    f.close()

    # TWL DICTIONARY
    f = open("data/lexica/twl.dat", "r", encoding="utf8")
    line = f.readline().strip("\n").split('	')
    while line != ['']:
        TWL[line[0]] = line[1:]
        line = f.readline().strip("\n").split('	')
    f.close()

    # CSW DICTIONARY
    f = open("data/lexica/csw.dat", "r")
    line = f.readline().strip("\n").split('	')
    while line != ['']:
        CSW[line[0]] = line[1:]
        line = f.readline().strip("\n").split('	')
    f.close()


open_files()
