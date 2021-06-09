import time
import pickle
import json
import struct
from time import sleep, time

from src.config import *


def convert_string_to_bytes(string):
    bytes = b''
    for i in string:
        bytes += struct.pack("B", ord(i))
    return bytes   


def current_milliseconds():
    return round(time() * 1000)


def serialize_game_objects(players, bullets):
    response_models = []
    for entity in bullets:
        entity_temp = {
            "type": "bullet",
            "centerx": entity.rect.centerx,
            "centery":  entity.rect.centery,
            "angle":  entity.angle
        }
        response_models.append(entity_temp)
    for entity in players:
        entity_temp = {
            "type": "player",
            "nickname": entity.nickname,
            "centerx": entity.rect.centerx,
            "centery":  entity.rect.centery,
            "angle":  entity.angle,
            "health": entity.health
        }
        response_models.append(entity_temp)
    return json.dumps(response_models)


def decode_msg_header(recv_data):
    data_rec = recv_data.decode('utf-8')
    data_rec = data_rec.split('\r\n\r\n')[0]
    data_array = data_rec.split('\r\n')
    data_values = {}
    for row in data_array:
        key = row.split(":", 1)[0]
        val = row.split(":", 1)[1]
        data_values[key] = val
        if key == data_header_code:
            break
    return data_values


def prepare_message(command=None, status=None, auth=None, data=''):
    header_msg = ''
    if command:
        header_msg += command_header_code + ":" + command

    if status:
        if len(header_msg) > 0: header_msg += soft_end
        header_msg += status_header_code + ":" + status    
    
    if auth:
        if len(header_msg) > 0: header_msg += soft_end
        header_msg += auth_header_code + ":" + auth
    
    if len(header_msg) > 0: header_msg += soft_end
    header_msg += lenght_header_code + ":" + str(len(str(data)))

    mess = header_msg + soft_end + data_header_code + ":" + str(data) + hard_end
    return mess.encode('utf-8') 


def recv_msg_from_socket(sock):
    data_rec = b''
    while b'\r\n\r\n' not in data_rec:
        data_rec = data_rec + sock.recv(1)

    headers = decode_msg_header(data_rec)
    data = headers[data_header_code]
    return headers, data


def recv_from_socket_to_pointer(_socket, value):
    while True:
        try:
            headers, data = recv_msg_from_socket(_socket)
            value[0] = ([headers, data])
        except:
            break


def send_to_socket_from_pointer(_socket, value):
    last_send_value = ''
    last_update_millis = current_milliseconds()
    while True:
        try:
            now_millis = current_milliseconds()
            if value[0] == None:
                break
            if last_send_value != value[0] or now_millis - last_update_millis > 1000 :
                newest_data = value[0]
                if newest_data != '':
                    _socket.send(newest_data)
                last_send_value = newest_data
                last_update_millis = now_millis
            sleep(1/20)
        except:
            break
