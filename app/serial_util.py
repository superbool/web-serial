# -*- encoding: utf8 -*-

import codecs
import os
import sys
import threading

import serial
from serial.tools.list_ports import comports
from serial.tools import hexlify_codec


class MySerial(object):
    RX_EOL_SEQ = b'\r\n'
    timeout = 1

    def __init__(self, port, baudrate=9600, rx_callback=None, *args, **kwargs):
        self.alive = False
        self.port = port
        self.baudrate = baudrate

        self._responseEvent = None  # threading.Event()
        self._expectResponseTermSeq = None  # expected response terminator sequence
        self._response = None  # Buffer containing response to a written command
        self._notification = []  # Buffer containing lines from an unsolicited notification from the modem
        # Reentrant lock for managing concurrent write access to the underlying serial port
        self._txLock = threading.RLock()

        self.rx_callback = rx_callback or self._default_callback

        self.com_args = args
        self.com_kwargs = kwargs

    def _default_callback(self, *args, **kwargs):
        """ Placeholder callback function (does nothing) """

    def connect(self):
        """ Connects to the device and starts the read thread """
        self.serial = serial.Serial(dsrdtr=True, rtscts=True, port=self.port, baudrate=self.baudrate,
                                    timeout=self.timeout, *self.com_args, **self.com_kwargs)
        self.alive = True
        # Start read thread
        self._start_reader()

    def close(self):
        """ Stops the read thread, waits for it to exit cleanly, then closes the underlying serial port """
        self._stop_reader()
        self.serial.close()
        self.alive = False

    def write(self, data):
        return self.serial.write(data)

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self._reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        if hasattr(self.serial, 'cancel_read'):
            self.serial.cancel_read()
        self.receiver_thread.join()

    def _reader(self):
        """loop and copy serial->console"""
        try:
            LINE_END_STR = bytearray(self.RX_EOL_SEQ)
            LINE_END_LEN = len(LINE_END_STR)
            rx_buffer = bytearray()
            while self.alive and self._reader_alive:
                data = self.serial.read(1)
                if len(data) != 0:  # check for timeout
                    rx_buffer.append(ord(data))
                    if rx_buffer[-LINE_END_LEN:] == LINE_END_STR:
                        # A line (or other logical segment) has been read
                        bytes = rx_buffer[:-LINE_END_LEN]
                        rx_buffer = bytearray()
                        if len(bytes) > 0:
                            self.rx_callback(bytes)
        except serial.SerialException:
            self.alive = False
            raise
