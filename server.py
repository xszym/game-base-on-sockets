# Import the pygame module
import pygame

# Import menu to pygame
import pygame_menu

from random import randrange
import math
import random
import string
import socket
import asyncio
import threading
import websockets
import pickle
from time import time, sleep
import uuid
import os
import json
import logging
logging.basicConfig(level=logging.INFO)
# from queue import Queue

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
from utils import serialize_game_objects, decode_msg_header, prepare_message, recv_msg_from_socket, convert_string_to_bytes
os.environ["SDL_VIDEODRIVER"] = "dummy"


AVAILABLE_GAMES = {}


def recv_from_socket_from_queue(_socket, value):
    while True:
        headers, data = recv_msg_from_socket(_socket)
        value[0] = ([headers, data])
        # sleep(1/15)


def send_to_socket_from_queue(_socket, value):
    while True:
        newest_data = value[0]
        if newest_data != '':
            _socket.send(newest_data)
        sleep(1/15)


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

        self.recv_from_last_value = ['']
        self.send_to_newest_value = ['']

        self.recv_from_thread = threading.Thread(target=recv_from_socket_from_queue, args=(self.socket, self.recv_from_last_value, ))
        self.send_to_thread = threading.Thread(target=send_to_socket_from_queue, args=(self.socket, self.send_to_newest_value, ))
        self.recv_from_thread.start()
        self.send_to_thread.start()

        self.nickname = 'Nickname'
        self.secret_key = '1234'

        self.player_game_object = Player(self.nickname, randrange(400) + 10, randrange(300) + 10, 0)

    def update(self):
        pass
        # TODO
        # self.player_input = self.recv_from_queue.get()

    def __del__(self):
        self.socket.close()
        # TODO pop from tank game 
        # self.recv_from_thread.exit()
        # self.send_to_thread.exit()


class TankGame():
    def __init__(self):
        self.join_code = '9Z1D' # TODO ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))

        self.socket = open_new_connection()
        self.connected_players = {}
        self.port = get_port_of_socket(self.socket)
        self.is_game_started = False
        self.status = "WAITING"

        global AVAILABLE_GAMES
        AVAILABLE_GAMES[self.join_code] = self
    
    def send_no_of_connected_players(self):
        # TODO - Send ilosc podlaczonych graczy
        no_of_players = len(self.connected_players)
        msg = prepare_message(command='UPDATE_CHANNEL',data=no_of_players)
        for p in self.connected_players:
            p.socket.sendall()
        
    def wait_for_players(self):
        while not self.is_game_started:
            client, addr = self.socket.accept()
            print("Connected: " + addr[0] + " to game " + self.join_code)
            new_player_profile = PlayerProfil(client)

            if len(self.connected_players) == 0:
                self.host_socket = new_player_profile
            
            self.connected_players[client] = new_player_profile # TODO - change key from client to auth
            print("len -> self.connected_players", len(self.connected_players))
            if len(self.connected_players) == 4: # TODO 2
                self.is_game_started = True # CZESC !!! Co mnie podglDądasz?DISKORD? DISKOROLKA?
            # TODO - send_no_of_connected_players(self)
            # TODO - dla hosta sprawdz czy wystartował grę :)
        self.status = "BUSY"

    def __del__(self):
        global AVAILABLE_GAMES
        AVAILABLE_GAMES.pop(self.join_code)
        self.socket.close()


def decode_json_data(string):
    msg = string[1]
    return json.loads(msg)


def start_the_game(host_client):
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    bullets = pygame.sprite.Group()

    tank_game = TankGame()
    msg = prepare_message(command='START_CHANNEL',status='SUCC',data=tank_game.join_code)
    host_client.sendall(msg)

    tank_game.wait_for_players()
    print("GAME STARTED")
    
    running = True
    while running:
        players_objects = pygame.sprite.Group()

        for key, player_profile in tank_game.connected_players.items():
            players_objects.add(player_profile.player_game_object)

            pressed_keys = player_profile.recv_from_last_value[0]
        
            if pressed_keys != '':
                pressed_keys = decode_json_data(pressed_keys)
                # pressed_keys = pressed_keys
                # print(pressed_keys)
                bullets = player_profile.player_game_object.update(pressed_keys, bullets)
            else:
                pressed_keys = pygame.key.get_pressed()
                bullets = player_profile.player_game_object.update(pressed_keys, bullets)

        bullets.update()

        objects_positions = serialize_game_objects(players_objects, bullets)
        msg = prepare_message(command='UPDATE_GAME',status='SUCC',data=objects_positions)
        
        for key, player_profile in tank_game.connected_players.items():
            player_profile.send_to_newest_value[0] = msg

        clock.tick(30)

    del tank_game


def get_random_uuid_for_player():
    return str(uuid.uuid4())


def on_new_client(client):
    while True:
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
            game_threat = threading.Thread(target=start_the_game, args=(client, ))
            game_threat.start()
            # break 
        elif command == 'JOIN_CHANNEL':
            global AVAILABLE_GAMES
            if data in AVAILABLE_GAMES:
                mess = prepare_message(command='JOIN_CHANNEL', status='SUCC', data=str(AVAILABLE_GAMES[data].port)) 
                client.sendall(mess)
            else:
                mess = prepare_message(command='JOIN_CHANNEL', status='ERR', data='GAME NOT EXITS') 
                client.sendall(mess)
        elif command == 'QUIT GAME':
            client.close()
            break

        else:
            mess = prepare_message('INVALID COMMAND','ERR','') 
            client.sendall(mess)
            # print('I send: ' + mess.decode('utf-8'))

        #------------
    # if command == 'QUIT GAME':
    #     mess = prepare_message('END GAME','SUCC','') 
    #     client.sendall(mess)
    #     print('I send: ' + mess.decode('utf-8'))
    # 
    # try:
    #     client.close()
    # except:
    #     pass


def main_server_loop():
    s = open_new_connection(MAIN_SERVER_SOCKET_PORT)
    while True:
        client, addr = s.accept()
        print("Connected: " + addr[0])
        threading.Thread(target=on_new_client, args=(client, )).start()
    s.close()


if __name__ == '__main__':
    main_server_loop()
