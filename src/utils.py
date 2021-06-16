import json
import struct
import time
from time import sleep, time

from src.config import *

ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def convert_string_to_bytes(string):
    bytes = b''
    for i in string:
        bytes += struct.pack("B", ord(i))
    return bytes


def current_milliseconds():
    return round(time() * 1000)


def decode_msg(recv_data):
    data_rec = recv_data.decode('utf-8')
    data_rec = data_rec.split(hard_end)[0]
    return data_rec


def prepare_standard_msg(command, auth=None, data=None):
    header_msg = command_header_code + ":" + command
    if auth:
        if len(header_msg) > 0: header_msg += soft_end
        header_msg += auth_header_code + ":" + auth
    if data:
        if len(header_msg) > 0: header_msg += soft_end
        header_msg += data_header_code + ":" + data
    mess = header_msg + hard_end
    return mess.encode('utf-8')


def decode_standard_msg(recv_data):
    data_rec = decode_msg(recv_data)
    data_array = data_rec.split(soft_end)
    headers = {}
    for row in data_array:
        key = row.split(":", 1)[0]
        val = row.split(":", 1)[1]
        headers[key] = val
        if key == data_header_code:
            break
    return headers


def prepare_game_msg(game_data):
    mess = str(game_data) + hard_end
    return mess.encode('utf-8')


def decode_game_msg(recv_data):
    game_data = json.loads(recv_data)
    return game_data


def prepare_status_msg(code, message='', data=''):
    mess = json.dumps({"code": code, "message": message, "data": data}) + hard_end
    return mess.encode('utf-8')


def decode_status_msg(recv_data):
    data_rec = decode_msg(recv_data)
    return json.loads(data_rec)


def recv_msg_from_socket(sock):
    data_rec = b''
    while hard_end.encode() not in data_rec:
        data_rec = data_rec + sock.recv(1)
    return data_rec
    # headers = decode_msg_header(data_rec)
    # data = headers[data_header_code]
    # return headers, data


def recv_from_socket_to_pointer(_socket, value):
    while True:
        try:
            data_rec = recv_msg_from_socket(_socket)
            data_rec = decode_msg(data_rec)
            value[0] = data_rec
        except:
            break


def send_to_socket_from_pointer(_socket, value):
    last_send_value = ''
    last_update_millis = current_milliseconds()
    while True:
        try:
            now_millis = current_milliseconds()
            if value[0] is None:
                break
            if last_send_value != value[0] or now_millis - last_update_millis > \
                    MAX_TIME_WITH_NO_SEND_TO_SOCKET_IN_GAME_IN_MILLIS:
                newest_data = value[0]
                if newest_data != '':
                    _socket.send(newest_data)
                last_send_value = newest_data
                last_update_millis = now_millis
            sleep(1 / 15)
        except:
            print("Broke connection on port")
            break
