#!/usr/bin/env python
from flask import Flask, render_template, session, request
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
    emit('server_response', {'data': msg['data']})


@app.route("/api/list/ports")
def list_ports():
    ports = []
    print('port list:')
    for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
        sys.stderr.write('{:2}:{:20}\n'.format(n, port))
        ports.append(port)
    return json.dumps({'data': ports})


@app.route("/api/open/port", methods=['POST'])
def open_port():
    print('open port:', request.form)
    port = request.form.get('port')
    baudrate = int(request.form.get('baudrate'))
    bytesizes = int(request.form.get('bytesizes'))
    stopbits = float(request.form.get('stopbits'))
    parities = request.form.get('parities')
    global my_serial
    if my_serial is not None:
        return json.dumps({'error': '端口已经打开'})
    my_serial = MySerial(port, baudrate=baudrate, rx_callback=rx_to_socket,
                         bytesize=bytesizes, parity=parities, stopbits=stopbits)
    my_serial.connect()
    return json.dumps({'data': True})


@app.route("/api/close/port", methods=['POST'])
def close_port():
    port = request.form.get('port')
    print('close port:', port)
    global my_serial
    my_serial.close()
    my_serial = None
    return json.dumps({'data': True})


@app.route("/api/write/data", methods=['POST'])
def write_data():
    data = request.form.get('data')
    print('write data:', data)
    global my_serial
    if my_serial is None:
        return json.dumps({'data': False})
    bytes_data = data.encode(encoding="utf-8")
    length = my_serial.write(bytes_data)
    return json.dumps({'data': length})


def rx_to_socket(bytes_data):
    print(bytes_data)
    data = bytes_data.decode('utf-8', errors='ignore')
    socketio.emit('server_response', {'data': data})


@socketio.on('serial_start_event')
def connected_msg(msg):
    emit('server_response', {'data': msg['data']})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
