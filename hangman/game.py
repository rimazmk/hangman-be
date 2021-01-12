"""Handle Game Logic."""

from . import GameState, Dict


def create_game(params: Dict[str, str]) -> GameState:
    """Create GameState object given initial game parameters."""
    if params['time'] == 'inf':
        time = None
    else:
        time = int(params['time'])

    return {
        'players': [params['username']],
        'wins': {params['username']: 0},
        'right': {params['username']: 0},
        'wrong': {params['username']: 0},
        'misses': {params['username']: 0},
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
        'numRounds': int(params['numRounds']),
        'time': time,
    }


def start_game(game_state: GameState) -> None:
    """Start the game and assign the first guesser."""
    game_state['gameStart'] = True
    game_state['guesser'] = game_state["players"][1]


def add_player(game_state: GameState, user: str) -> None:
    """Add a new player to the game."""
    game_state['players'].append(user)
    game_state['wins'][user] = game_state['right'][user] = game_state['wrong'][user] = game_state['misses'][user] = 0


def remove_player(game_state: GameState, user: str) -> None:
    """Remove a player from the game if they exist."""
    try:
        game_state['players'].remove(user)
        game_state['wins'].pop(user)
        game_state['right'].pop(user)
        game_state['wrong'].pop(user)
        game_state['misses'].pop(user)
        print(user, " has left the room")
    except (ValueError, KeyError):
        print("No user found named ", user)


def num_players(game_state: GameState) -> int:
    """Return the number of players in the game."""
    return len(game_state['players'])


def set_new_guesser(game_state: GameState) -> None:
    """Assign the next guesser."""
    guess_pos = game_state['players'].index(game_state['guesser'])

    while True:
        guess_pos = (guess_pos + 1) % num_players(game_state)

        if game_state['players'][guess_pos] != game_state['hanger']:
            break

    game_state['guesser'] = game_state['players'][guess_pos]


def handle_leave(game_state: GameState, username: str) -> None:
    """Update GameState object to reflect player leaving."""
    if num_players(game_state) == 2:
        remove_player(game_state, username)
        time = 'inf' if not game_state['time'] else game_state['time']
        res = create_game({
            'username': game_state['players'][0],
            'lives': game_state['lives'],
            'rotation': game_state['rotation'],
            'numRounds': game_state['numRounds'],
            'time': time,
        })
        game_state.update(res)
        # Is this necessary?
        game_state['wins'] = {game_state['players'][0]: 0}
        game_state['right'] = {game_state['players'][0]: 0}
        game_state['wrong'] = {game_state['players'][0]: 0}
        game_state['misses'] = {game_state['players'][0]: 0}

    elif username == game_state['hanger']:
        remove_player(game_state, username)
        game_state['hanger'] = game_state['players'][0]
        game_state['guesser'] = game_state['players'][1]
        game_state['word'] = game_state['category'] = ""

    elif username == game_state['guesser']:
        set_new_guesser(game_state)
        remove_player(game_state, username)

    else:
        remove_player(game_state, username)


def handle_new_round(game_state: GameState, category: str,
                     word: str, user: str) -> None:
    """Update GameState object for the new round."""
    game_state['word'] = word
    game_state['category'] = category
    game_state['guessedWord'] = ''.join(
        ['_' if c.isalnum() else c for c in word])

    if game_state['round']:
        if game_state['rotation'] == 'robin':
            hang_pos = game_state['players'].index(game_state['hanger'])
            next_hanger = hang_pos + \
                1 if hang_pos != (num_players(game_state) - 1) else 0
            game_state['hanger'] = game_state['players'][next_hanger]
        elif game_state["numIncorrect"] != game_state['lives']:
            game_state["hanger"] = user

        hang_pos = game_state['players'].index(game_state['hanger'])
        guess_pos = hang_pos + \
            1 if hang_pos != (num_players(game_state) - 1) else 0
        game_state['guesser'] = game_state['players'][guess_pos]

    game_state['numIncorrect'] = 0
    game_state['round'] += 1


def guess(game_state: GameState):
    """Handle player's guess."""
    cur = game_state['curGuess']
    status = None

    if not cur:
        game_state['numIncorrect'] += 1
        game_state['misses'][game_state['guesser']] += 1
        status = "timer"

    elif len(cur) == 1:
        game_state['guessedLetters'].append(cur)
        match = 0

        for i, (word_let, guess_let) in enumerate(
                zip(game_state['word'], game_state['guessedWord'])):
            if word_let.lower() == cur and guess_let == '_':
                game_state['guessedWord'] = game_state['guessedWord'][:i] + \
                    word_let + game_state['guessedWord'][i + 1:]
                match += 1

        if match == 0:
            game_state['numIncorrect'] += 1
            game_state['wrong'][game_state['guesser']] += 1
            status = "incorrect"
        else:
            game_state['right'][game_state['guesser']] += 1
            status = "correct"

    else:
        game_state['guessedWords'].append(cur)

        if cur.lower() != game_state['word'].lower():
            game_state['numIncorrect'] += 1
            game_state['wrong'][game_state['guesser']] += 1
            status = "incorrect"

    if ((cur and cur.lower() == game_state['word'].lower())
            or game_state['numIncorrect'] == game_state['lives'] or
            game_state['word'].lower() == game_state['guessedWord'].lower()):

        if game_state['numIncorrect'] == game_state['lives']:
            game_state['wins'][game_state['hanger']] += 1
        else:
            game_state['wins'][game_state['guesser']] += 1

        # TODO: Transition to newRound without relying on category
        game_state['category'] = game_state['curGuess'] = game_state[
            'guessedWord'] = ""
        game_state['guessedLetters'], game_state['guessedWords'] = [], []

        status = "win"
    else:
        set_new_guesser(game_state)

    return status
