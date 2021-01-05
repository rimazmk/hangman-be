"""Handle Database Operations."""

from typing import Optional
from . import GameState, mongo


def upsert(roomID: str, game_state: GameState) -> None:
    """
    Update gameState from roomID if it already exists.
    Otherwise, insert roomID and gameState into database.
    """
    mongo.db.hangman.update({"roomID": roomID}, {
        "roomID": roomID,
        "gameState": game_state
    },
        upsert=True)


def get(roomID: str) -> Optional(GameState):
    """Get gameState from the database if it exists."""
    res = mongo.db.hangman.find_one({"roomID": roomID})

    if res:
        return res['gameState']
    return None


def exists(roomID: str) -> bool:
    """Check if the given roomID exists in the database."""
    return mongo.db.hangman.count_documents({'roomID': roomID}, limit=1) > 0


def delete(roomID: str) -> None:
    """Delete roomID from database."""
    mongo.db.hangman.remove({"roomID": roomID})
