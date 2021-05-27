# Import the pygame module
import pygame

# Import menu to pygame
import pygame_menu

import math
import random
import string
import socket
import asyncio
import threading
import websockets
import pickle
from time import time
import uuid
import os
import json
import logging
logging.basicConfig(level=logging.INFO)
from queue import Queue

from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)

from config import *
from game_classes import Player, Bullet
from utils import serialize_game_objects, decode_msg_header, prepare_message, recv_msg_from_socket
os.environ["SDL_VIDEODRIVER"] = "dummy"


# TODO - python queue with one element
def recv_from_socket_from_queue(_socket, _queue):
    while True:
        # TODO - data = socket.recv() / Change
        recived_msg_from_player =  _socket.recv(RECV_BUFFOR_SIZE)
        if len(recived_msg_from_player) > 0:
            print("recived", recived_msg_from_player)
        
        # if recived_msg_from_player == "None":
        #     pass
        # elif recived_msg_from_player != "None":
        #     data = pickle.loads(recived_msg_from_player)
        #     _queue.put(data)


def send_to_socket_from_queue(_socket, _queue):
    while True:
        # TODO - socket.send(data) / Change
        _socket.send("dupa".encode('utf-8'))
        if _queue.empty():
            pass
            # _socket.send('None')
        else:
            data = _queue.get()
            print("send", data)
            _socket.send(data)


def get_port_of_socket(sock):
    return sock.getsockname()[1]


def open_new_connection(port=0):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind((SERVER_IP, port))
    sock.listen(SERVER_NO_OF_QUEUED_CONNECTIONS)
    print("Starting new connection at port", get_port_of_socket(sock))
    return sock


class PlayerProfil():
    def __init__(self, client_socket):
        self.socket = client_socket
        self.socket_port = get_port_of_socket(self.socket)

        self.recv_from_queue = Queue()
        self.send_to_queue = Queue()

        self.recv_from_thread = threading.Thread(target=recv_from_socket_from_queue, args=(self.socket, self.recv_from_queue, ))
        self.send_to_thread = threading.Thread(target=send_to_socket_from_queue, args=(self.socket, self.send_to_queue, ))
        self.recv_from_thread.start()
        self.send_to_thread.start()

        self.nickname = 'Nickname'
        self.secret_key = '1234'

        self.player_game_object = Player(self.nickname, 10, 10, 0)

    def update(self):
        pass
        # TODO
        # self.player_input = self.recv_from_queue.get()

    def __del__(self):
        self.socket.close()
        # self.recv_from_thread.exit()
        # self.send_to_thread.exit()


class TankGame():
    def __init__(self):
        # self.join_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        
        self.socket = open_new_connection()
        self.connected_players = {}
        self.port = get_port_of_socket(self.socket)
        self.is_game_started = False

    def start_game(self):
        pass

    def update(self):
        pass


def start_the_game(host_client):
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    bullets = pygame.sprite.Group()
    players = pygame.sprite.Group()

    tank_game = TankGame()
    msg = prepare_message(command='START_CHANNEL',status='SUCC',data=tank_game.port)
    host_client.sendall(msg)
    host_client.close()

    while not tank_game.is_game_started:
        client, addr = tank_game.socket.accept()
        print("Connected: " + addr[0])
        new_player_profile = PlayerProfil(client)

        if len(tank_game.connected_players) == 0:
            tank_game.host_socket = new_player_profile
        
        tank_game.connected_players['api_key'] = ''
        # TODO - Send ilosc podlaczonych graczy
        # TODO - dla hosta sprawdz czy wystartował grę :) 

    running = True
    while running:
        for key, player_profile in tank_game.connected_players.items():
            pressed_keys = None
            if not player_profile.recv_from_queue.empty():
                pressed_keys = player_profile.recv_from_queue.get()

            if pressed_keys != None:
                bullets = player_profile.player_game_object.update(pressed_keys, bullets)
            else:
                pressed_keys = pygame.key.get_pressed()
                bullets = player_profile.player_game_object.update(pressed_keys, bullets)

        bullets.update()

        objects_positions = serialize_game_objects(players, bullets)
        for player in players:
            player.send_to_queue(objects_positions)

        clock.tick(30)


def get_random_uuid_for_player():
    print(str(uuid.uuid4()))
    return str(uuid.uuid4())


def on_new_client(client):
    while True:
        headers, data = recv_msg_from_socket(client)
        command = headers.get('Command')
        if command == 'REGISTER':
            login = get_random_uuid_for_player()

            if headers.get('Auth') == 'None':
                mess = prepare_message(command='REGISTER',status='SUCC',data=login)
                print('I send: ' + mess.decode('utf-8'))
            else:
                mess = prepare_message(command='REGISTER',status='ERR')

            client.sendall(mess)
            print('I send: ' + mess.decode('utf-8'))
        elif command == 'START_CHANNEL':
            game_threat = threading.Thread(target=start_the_game, args=(client, ))
            game_threat.start()
            break 
        elif command == 'QUIT GAME':
            client.close()
            break

        else:
            mess = prepare_message('INVALID COMMAND','ERR','') 
            client.sendall(mess)
            print('I send: ' + mess.decode('utf-8'))

        #------------
    # if command == 'QUIT GAME':
    #     mess = prepare_message('END GAME','SUCC','') 
    #     client.sendall(mess)
    #     print('I send: ' + mess.decode('utf-8'))
    # client.close()


def main_server_loop():
    s = open_new_connection(MAIN_SERVER_SOCKET_PORT)
    while True:
        client, addr = s.accept()
        print("Connected: " + addr[0])
        threading.Thread(target=on_new_client, args=(client, )).start()
    s.close()


if __name__ == '__main__':
    main_server_loop()
