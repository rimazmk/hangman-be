import json


def create_game(params):
    def_game_state = {
        'players': [params['username']],
        'wins': {params['username']: 0},
        'hanger': params['username'],
        'category': "",
        'word': "",
        'guessedLetters': [],
        'numIncorrect': 0,
        'lives': int(params['lives']),
        'guessedWords': [],
        'guesser': "",
        'curGuess': "",
        'guessedWord': "",
        'gameStart': False,
        'cap': 8,
        'rotation': params['rotation'],
        'round': 0,
        'numrounds': int(params['numrounds'])
    }
    return def_game_state


def start_game(game_state):
    game_state['gameStart'] = True
    game_state['guesser'] = game_state["players"][1]


def add_player(game_state, user):
    game_state['players'].append(user)
    game_state['wins'].update({user: 0})


def remove_player(game_state, user):
    try:
        game_state['players'].remove(user)
        game_state['wins'].pop(user)
        print(user, " has left the room")
    except ValueError:
        print("no user found named ", user)


def num_players(game_state):
    return len(game_state['players'])


def set_new_guesser(game_state, username):
    if num_players(game_state) == 2:
        remove_player(game_state, username)
        res = create_game({
            'username': game_state['players'][0],
            'lives': game_state['lives'],
            'rotation': game_state['rotation'],
        })
        game_state.update(res)

    elif username == game_state['hanger']:
        remove_player(game_state, username)
        game_state['hanger'] = game_state['players'][0]
        game_state['guesser'] = game_state['players'][1]
        game_state['word'] = game_state['category'] = ""

    elif username == game_state['guesser']:
        guess_pos = game_state['players'].index(game_state['guesser'])
        next_guesser = (guess_pos + 1) % len(game_state['players'])
        jump = (next_guesser + 1) % len(game_state['players'])
        guess_pos = next_guesser if game_state['hanger'] != game_state[
            'players'][next_guesser] else jump
        game_state['guesser'] = game_state['players'][guess_pos]
        remove_player(game_state, username)

    else:
        remove_player(game_state, username)


def handle_new_round(game_state, category, word, user, roomID):
    game_state['word'] = word
    game_state['category'] = category
    game_state['guessedWord'] = ''.join(
        ['#' if c.isalnum() else c for c in word])

    if game_state['round']:
        if game_state['rotation'] == 'robin':
            hang_pos = game_state['players'].index(game_state['hanger'])
            next = hang_pos + \
                1 if hang_pos != (len(game_state['players']) - 1) else 0
            game_state['hanger'] = game_state['players'][next]
        elif game_state["numIncorrect"] != game_state['lives']:
            game_state["hanger"] = user

        hang_pos = game_state['players'].index(game_state['hanger'])
        guess_pos = hang_pos + \
            1 if hang_pos != (len(game_state['players']) - 1) else 0
        game_state['guesser'] = game_state['players'][guess_pos]

    game_state['numIncorrect'] = 0
    game_state['round'] += 1


def guess(game_state):
    cur = game_state['curGuess']

    if len(cur) == 1 and cur.isalpha():
        game_state['guessedLetters'].append(cur.lower())
        match = 0

        for i, (w, g) in enumerate(
                zip(game_state['word'], game_state['guessedWord'])):
            if w.lower() == cur.lower() and g == '#':
                game_state['guessedWord'] = game_state['guessedWord'][:i] + \
                    cur + game_state['guessedWord'][i + 1:]
                match += 1

        if match == 0:
            game_state['numIncorrect'] += 1

    else:
        game_state['guessedWords'].append(cur)

        if cur.lower() != game_state['word'].lower():
            game_state['numIncorrect'] += 1

    # TODO: Update wins variable here
    if (cur.lower() == game_state['word'].lower()
            or game_state['numIncorrect'] == game_state['lives'] or
            game_state['word'].lower() == game_state['guessedWord'].lower()):

        # TODO: Transition to newRound without relying on category
        # game_state['word'] = ""
        if game_state['numIncorrect'] == game_state['lives']:
            game_state['wins'][game_state['hanger']] += 1
        else:
            game_state['wins'][game_state['guesser']] += 1

        game_state['category'] = game_state['curGuess'] = game_state[
            'guessedWord'] = ""
        game_state['guessedLetters'], game_state['guessedWords'] = [], []
    else:
        guess_pos = game_state['players'].index(game_state['guesser'])
        guess_pos = (guess_pos + 1) % len(game_state['players'])
        hang_pos = game_state['players'].index(game_state['hanger'])

        if guess_pos == hang_pos:
            guess_pos = (guess_pos + 1) % len(game_state['players'])
        game_state['guesser'] = game_state['players'][guess_pos]
