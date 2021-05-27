import socket
import os.path
import random 
import time
import uuid
from utils import prepare_message, recv_msg_from_socket
from config import *
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random

counter = os.urandom(16) #CTR counter string value with length of 16 bytes.
key = os.urandom(32)

def get_random_uuid_for_player():
    print(str(uuid.uuid4()))
    return str(uuid.uuid4())

def generate_public_key():
    random_generator = Random.new().read
    key = RSA.generate(1024,random_generator) 
    public = key.publickey().exportKey()
    #????????????????????????????????? help 
    hash_object = hashlib.sha1(public) 
    hex_digest = hash_object.hexdigest()
    

def do_encrypt(message):
    obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    ciphertext = obj.encrypt(message)
    return ciphertext

def do_decrypt(ciphertext):
    obj2 = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    message = obj2.decrypt(ciphertext)
    return message

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("localhost", MAIN_SERVER_SOCKET_PORT))
s.listen(5)

player_list = ['']

while True:
    client, addr = s.accept()
    print("Connected: " + addr[0])

    headers, data = recv_msg_from_socket(client)
    command = headers.get('Command')

    # TODO - Check if auth and auth correct ;) 

    if command == 'REGISTER':
        login = get_random_uuid_for_player()
        mess = prepare_message(command='REGISTER',status='SUCC',data=login)
        # print('I send: ' + mess.decode('utf-8'))

        # TODO - Zpisywanie do plaintext zarejstrowanych USSID
        # mess = prepare_message(command='REGISTER',status='ERR')

        client.sendall(mess)
    elif command == 'START_CHANNEL':
        print("STARTING GAME")
        # game_threat = threading.Thread(target=start_the_game, args=(client, ))
        # game_threat.start()
        break 
    elif command == 'JOIN_CHANNEL':
        global AVAILABLE_GAMES
        if data in AVAILABLE_GAMES:
            mess = prepare_message(command='JOIN_CHANNEL', status='SUCC', data=AVAILABLE_GAMES[data].port) 
            client.sendall(do_encrypt(mess))
        else:
            mess = prepare_message(command='JOIN_CHANNEL', status='ERR', data='GAME NOT EXITS') 
            client.sendall(do_encrypt(mess))
    elif command == 'QUIT GAME':
        client.close()
        break

    else:
        mess = prepare_message('INVALID COMMAND','ERR','') 
        client.sendall(do_encrypt(mess))
        # print('I send: ' + mess.decode('utf-8'))

    #------------
# if command == 'QUIT GAME':
#     mess = prepare_message('END GAME','SUCC','') 
#     client.sendall(mess)
#     print('I send: ' + mess.decode('utf-8'))
# 
try:
    client.close()
except:
    pass



s.close()