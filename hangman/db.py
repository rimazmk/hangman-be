from . import redis_client
import json


def set(roomID, game_state):
    redis_client.set(roomID, json.dumps(game_state))


def get(roomID):
    return json.loads(redis_client.get(roomID))


def exists(roomID):
    return redis_client.exists(roomID)


def delete(roomID):
    return redis_client.delete(roomID)
