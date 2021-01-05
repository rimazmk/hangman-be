from . import mongo


def set(roomID, game_state):
    mongo.db.hangman.update({"roomID": roomID}, {
        "roomID": roomID,
        "gameState": game_state
    },
        upsert=True)


def get(roomID):
    res = mongo.db.hangman.find_one({"roomID": roomID})

    if res:
        return res['gameState']
    return None


def exists(roomID):
    return mongo.db.hangman.count_documents({'roomID': roomID}, limit=1)


def delete(roomID):
    mongo.db.hangman.remove({"roomID": roomID})
