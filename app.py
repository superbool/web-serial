#!/usr/bin/env python
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit
from serial.tools.list_ports import comports
import sys, json
from serial_util import MySerial

app = Flask(__name__, template_folder='./templates')
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

my_serial = None


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('client_event')
def client_msg(msg):
    emit('server_response', {'data': msg['data']})


@socketio.on('connect_event')
def connected_msg(msg):
    # port = '/dev/cu.usbserial-1410'
    # global my_serial
    # my_serial = MySerial(port, rx_callback=socket_rx)
    # my_serial.connect()
    # return render_template('index.html')
    emit('server_response', {'data': msg['data']})


@app.route("/api/list/ports")
def list_ports():
    ports = []
    for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
        sys.stderr.write('--- {:2}: {:20} {!r}\n'.format(n, port, desc))
        ports.append(port)
    return json.dumps({'data': ports})


@app.route("/api/start/port")
def open_port():
    port = request.args.get('port')

    global my_serial
    my_serial = MySerial(port, rx_callback=socket_rx)
    my_serial.connect()
    return render_template('index.html')


def socket_rx(bytes):
    with app.test_request_context('/'):
        data = bytes.decode('utf-8', errors='ignore')
        socketio.emit('server_response', {'data': data})


@socketio.on('serial_start_event')
def connected_msg(msg):
    emit('server_response', {'data': msg['data']})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
