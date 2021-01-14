import os
from hangman import app, socketio

port = os.environ.get("PORT") 

if __name__ == "__main__":
    socketio.run(app, debug=False)
