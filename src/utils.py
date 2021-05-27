import time
import pickle
import json
import struct

from src.config import *


def convert_string_to_bytes(string):
    bytes = b''
    for i in string:
        bytes += struct.pack("B", ord(i))
    return bytes   


def do_decrypt(ciphertext):
    obj2 = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    message = obj2.decrypt(ciphertext)
    return message



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
            "angle":  entity.angle
        }
        response_models.append(entity_temp)
    return json.dumps(response_models)


def decode_msg_header(recv_data):
    data_rec = recv_data.decode('utf-8')
    data_rec = data_rec.split('\r\n\r\n')[0]
    data_array = data_rec.split('\r\n')
    data_values = {value.split(":")[0]: value.split(":")[1] for value in data_array}
    return data_values


def prepare_message_enc(command=None, status=None, auth=None, data=''):
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
    header_msg += lenght_header_code + ":" + str(len(data))

    mess = header_msg + hard_end + str(data) + hard_end
    #print("\n", "Prepere msg", mess.strip()) 
    return mess.encode('utf-8') 

def recv_msg_from_socket_enc(sock):
    data_rec = b''
    while b'\r\n\r\n' not in data_rec:
        data_rec = data_rec + sock.recv(1)

    headers = decode_msg_header(do_decrypt(data_rec))

    data_rec_second_part = data_rec
    lenght_value = int(headers['Lenght'])
    length = len(data_rec.decode('utf-8').split('\r\n\r\n')[0]) + 4
    while len(data_rec_second_part) < length + lenght_value + 4:
        data_rec_second_part = data_rec_second_part + sock.recv(1)

    data_rec_second_part = do_decrypt(data_rec_second_part)
    data = data_rec_second_part.decode('utf-8').split('\r\n\r\n')[1]
    # print('\n', "recv_msg ", headers, data.strip())
    return headers, data


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

    mess = header_msg + hard_end + str(data) + hard_end
    # print("\n", "Prepere msg", mess.strip()) 
    return mess.encode('utf-8') 


def recv_msg_from_socket(sock):
    data_rec = b''
    while b'\r\n\r\n' not in data_rec:
        data_rec = data_rec + sock.recv(1)

    headers = decode_msg_header(data_rec)

    data_rec_second_part = data_rec
    lenght_value = int(headers['Lenght'])
    length = len(data_rec.decode('utf-8').split('\r\n\r\n')[0]) + 4
    while len(data_rec_second_part) < length + lenght_value + 4:
        data_rec_second_part = data_rec_second_part + sock.recv(1)
    data = data_rec_second_part.decode('utf-8').split('\r\n\r\n')[1]
    # print('\n', "recv_msg ", headers, data.strip())
    return headers, data


def recv_from_socket_to_pointer(_socket, value):
    while True:
        headers, data = recv_msg_from_socket(_socket)
        value[0] = ([headers, data])


def send_to_socket_from_pointer(_socket, value):
    while True:
        newest_data = value[0]
        if newest_data != '':
            _socket.send(newest_data)
        sleep(1/30)
