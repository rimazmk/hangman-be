from . import socketio, redis_client
from flask_socketio import emit
import json


@socketio.on('chat')
def handle_message(info):
    res = [info['user'], info['message']]
    emit('chat', res, room=info['roomID'], include_self=False)


@socketio.on('newRound')
def handle_new_round(info):
    word, roomID = info['word'], info['roomID']
    game_state = json.loads(redis_client.get(roomID))
    game_state['word'] = word
    game_state['category'] = info['category']
    game_state['guessedWord'] = ''.join(
        ['#' if c.isalnum() else c for c in word])
    redis_client.set(roomID, json.dumps(game_state))
    emit('response', game_state, room=roomID)


@socketio.on('guess')
def handle_guess(msg):
    game_state = msg['gameState']
    cur = game_state['curGuess']

    if len(cur) == 1 and cur.isalpha():
        game_state['guessedLetters'].append(cur.lower())
        match = 0

        for i, (w, g) in enumerate(zip(game_state['word'], game_state['guessedWord'])):
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
    if (cur.lower() == game_state['word'].lower() or
        game_state['numIncorrect'] == game_state['lives'] or
            game_state['word'].lower() == game_state['guessedWord'].lower()):

        if game_state["numIncorrect"] != game_state['lives']:
            game_state["hanger"] = msg['user']

        hang_pos = game_state['players'].index(game_state['hanger'])
        guess_pos = hang_pos + \
            1 if hang_pos != (len(game_state['players']) - 1) else 0
        game_state['guesser'] = game_state['players'][guess_pos]

        # TODO: Transition to newRound without relying on category
        # game_state['word'] = ""
        game_state['category'] = game_state['curGuess'] = game_state['guessedWord'] = ""
        game_state['guessedLetters'], game_state['guessedWords'] = [], []
        game_state['numIncorrect'] = 0
    else:
        guess_pos = game_state['players'].index(game_state['guesser'])
        guess_pos = (guess_pos + 1) % len(game_state['players'])
        hang_pos = game_state['players'].index(game_state['hanger'])

        if guess_pos == hang_pos:
            guess_pos = (guess_pos + 1) % len(game_state['players'])
        game_state['guesser'] = game_state['players'][guess_pos]

    redis_client.set(msg['roomID'], json.dumps(game_state))
    emit('update', game_state, room=msg['roomID'])
