import time
import pickle

from config import *

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
    return response_models


def decode_msg_header(recv_data):
    data_rec = recv_data.decode('utf-8')
    data_rec = data_rec.split('\r\n\r\n')[0]

    data_array = data_rec.split('\r\n')
    data_values = {value.split(":")[0]: value.split(":")[1] for value in data_array}
    return data_values

command_code = 'Command:'
status_code = 'Status:'
lenght_code = 'Lenght:'
auth_code = 'Auth:'
lenght_code = 'Lenght:'
def prepare_message(command=None, status=None, auth=None, data=''):
	header_msg = ''
	if command:
		header_msg += command_code + command

	if status:
		if len(header_msg) > 0: header_msg += soft_end
		header_msg += status_code + status	
	
	if auth:
		if len(header_msg) > 0: header_msg += soft_end
		header_msg += auth_code + auth
	
	if len(header_msg) > 0: header_msg += soft_end
	header_msg += lenght_code + str(len(str(data)))

	mess = header_msg + hard_end + str(data) + hard_end
	# print("Decode msg", mess)
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
    return headers, data
