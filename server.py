import pygame
from random import randrange
import math
import random
import string
import socket

import asyncio
from concurrent.futures import ThreadPoolExecutor 

import threading
import pickle
from time import time, sleep
import uuid
import os
import json
import logging
logging.basicConfig(level=logging.INFO)

from pygame.locals import (
    QUIT,
)

from src.config import *
from src.game_classes import Player, Bullet
from src.utils import serialize_game_objects, decode_msg_header, prepare_message, recv_msg_from_socket, convert_string_to_bytes, recv_from_socket_to_pointer, send_to_socket_from_pointer
os.environ["SDL_VIDEODRIVER"] = "dummy"


AVAILABLE_GAMES = {}


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

        self.recv_from_thread = threading.Thread(target=recv_from_socket_to_pointer, args=(self.socket, self.recv_from_last_value, ))
        self.send_to_thread = threading.Thread(target=send_to_socket_from_pointer, args=(self.socket, self.send_to_newest_value, ))
        self.recv_from_thread.start()
        self.send_to_thread.start()

        self.nickname = 'Nickname'
        self.secret_key = '1234'

        self.player_game_object = Player(self.nickname, randrange(400) + 10, randrange(300) + 10, 0)

    def update(self):
        pass

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
            if len(self.connected_players) == 2: # TODO - start na przycisk
                self.is_game_started = True
            # TODO - send_no_of_connected_players(self)
            # TODO - dla hosta sprawdz czy wystartowal grę :)
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
                bullets = player_profile.player_game_object.update(pressed_keys, bullets, players_objects)
            else:
                pressed_keys = pygame.key.get_pressed()
                bullets = player_profile.player_game_object.update(pressed_keys, bullets, players_objects)

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

            # TODO - Zpisywanie do plaintext zarejstrowanych USSID
            # mess = prepare_message(command='REGISTER',status='ERR')

            client.sendall(mess)
        elif command == 'START_CHANNEL':
            game_threat = threading.Thread(target=start_the_game, args=(client, ))
            game_threat.start()
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
    
    client.close()


def main_server_loop():
    s = open_new_connection(MAIN_SERVER_SOCKET_PORT)
    while True:
        client, addr = s.accept()
        print("Connected: " + addr[0])
        threading.Thread(target=on_new_client, args=(client, )).start()
    s.close()


def parse_recvd_data(data):
    """ Break up raw received data into messages, delimited
        by null byte """
    parts = data.split(b'\r\n\r\n')
    msgs = parts[:-1]
    rest = parts[-1]
    return (msgs, rest)


clients = []
class TankGameServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        """ Called on instantiation, when new client connects """
        self.transport = transport
        self.addr = transport.get_extra_info('peername')
        self._rest = b''
        self.name = None
        clients.append(self)
        print('Connection from {}'.format(self.addr))
    
    def data_received(self, data):
        """ Handle data as it's received. Broadcast complete
        messages to all other clients """
        data = self._rest + data
        (msgs, rest) = parse_recvd_data(data)
        self._rest = rest

        for msg in msgs:
            try:
                headers = decode_msg_header(msg)
                print(headers)
            except:
                print("Something not yes")
        #     msg = msg.decode('utf-8')
        #     if msg.isdigit():
        #         n = int(msg)
        #         task = asyncio.create_task(self.async_fib(n))
        #     else:
        #         msg = "Input digit"
        #         msg = prep_msg(msg)
        #         self.transport.write(msg)
        
    def connection_lost(self, ex):
        """ Called on client disconnect. Clean up client state """
        print('Client {} disconnected'.format(self.addr))
        clients.remove(self)

    # async def async_fib(self, n):
    #     task = await loop.run_in_executor(thread_pool, recur_fibo, n)
    #     response = str(task).encode()
    #     msg = f"fib({n})={response}"
    #     msg = prep_msg(msg)
    #     self.transport.write(msg)


# thread_pool = ThreadPoolExecutor()
# loop = asyncio.get_event_loop()

# # Create server and initialize on the event loop
# coroutine = loop.create_server(TankGameServerProtocol, host='0.0.0.0', port=MAIN_SERVER_SOCKET_PORT)
# server = loop.run_until_complete(coroutine)

# # print listening socket info
# for socket in server.sockets:
#     addr = socket.getsockname()
#     print('Listening on {}'.format(addr))

# # Run the loop to process client connections
# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     pass

# server.close()
# loop.run_until_complete(server.wait_closed())
# loop.close()

if __name__ == '__main__':
    main_server_loop()
