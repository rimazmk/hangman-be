from . import mongo


def set(roomID, game_state):
    mongo.db.hangman.update({"roomID": roomID}, {
        "roomID": roomID,
        "gameState": game_state
    },
                            upsert=True)


def get(roomID):
    res = mongo.db.hangman.find_one({"roomID": roomID})
    print(f"FROM GET: {res}")
    if res:
        return res['gameState']
    return None


def exists(roomID):
    return get(roomID) != None
    # mongo.db.hangman.find_one({
    #     "roomID": { "$in": [roomID], "$exists": True }
    # })


def delete(roomID):
    mongo.db.hangman.remove({"roomID": roomID})
