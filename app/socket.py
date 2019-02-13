# -*- encoding: utf8 -*-

from flask_socketio import emit
from app import socketio
import logging

logger = logging.getLogger(__name__)


@socketio.on('client_event')
def client_msg(msg):
    emit('server_response', {'data': msg['data']})


@socketio.on('connect_event')
def connected_msg(msg):
    emit('server_response', {'data': msg['data']})


@socketio.on('serial_start_event')
def connected_msg(msg):
    emit('server_response', {'data': msg['data']})


def rx_to_socket(bytes_data):
    logging.info(bytes_data)
    data = bytes_data.decode('utf-8', errors='ignore')
    socketio.emit('server_response', {'data': data})
