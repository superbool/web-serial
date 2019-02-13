# -*- encoding: utf8 -*-
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

FORMAT = '%(asctime)s - %(message)s'
import logging

logging.basicConfig(level=logging.INFO, format=FORMAT)

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

from app import socket
from app import api
