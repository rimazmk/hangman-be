from flask import Flask

app = Flask(__name__)

import hangman.sockets 
import hangman.server
