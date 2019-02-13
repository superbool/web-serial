# -*- encoding: utf8 -*-

from flask import Flask, render_template, request, jsonify
from serial.tools.list_ports import comports
import sys, json
from .serial_util import MySerial
import logging
from .socket import rx_to_socket
from app import app

logger = logging.getLogger(__name__)

my_serial = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/api/list/ports")
def list_ports():
    ports = []
    logger.info('port list:')
    for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
        logger.info('{:2}:{:20}\n'.format(n, port))
        ports.append(port)
    return jsonify({'data': ports})


@app.route("/api/open/port", methods=['POST'])
def open_port():
    logger.info('request data:%s', request.form.to_dict())
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
    return jsonify({'data': True})


@app.route("/api/close/port", methods=['POST'])
def close_port():
    port = request.form.get('port')
    logger.info('request data:%s', port)
    global my_serial
    my_serial.close()
    my_serial = None
    return jsonify({'data': True})


@app.route("/api/write/data", methods=['POST'])
def write_data():
    logger.info('request data:%s', request.form.to_dict())
    data = request.form.get('data')
    end_line = request.form.get('end_line')
    global my_serial
    if my_serial is None:
        return json.dumps({'data': False})
    bytes_data = data.encode(encoding="utf-8")
    if end_line == 'rn':
        bytes_data += b'\r\n'
    elif end_line == 'r':
        bytes_data += b'\r'
    logger.info('write byte data:%s', bytes_data)
    length = my_serial.write(bytes_data)
    return jsonify({'data': length})
