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
from src.utils import serialize_game_objects, decode_msg_header, prepare_message, recv_msg_from_socket, convert_string_to_bytes, recv_from_socket_to_pointer, send_to_socket_from_pointer, ordinal
os.environ["SDL_VIDEODRIVER"] = "dummy"


AVAILABLE_GAMES = {}


def get_port_of_socket(sock):
    return sock.getsockname()[1]


def open_new_connection(port=0):
    sock = None
    if port == 0:
        while True:
            try:
                new_port = random.randrange(MIN_PORT, MAX_PORT)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('0.0.0.0', new_port))
                sock.listen(SERVER_NO_OF_QUEUED_CONNECTIONS)
                break
            except:
                pass
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.listen(SERVER_NO_OF_QUEUED_CONNECTIONS)
    print("Starting new connection at port", get_port_of_socket(sock))
    return sock


class PlayerProfil():
    def __init__(self, client_socket, connected_players_profiles, nickname='nickname'):
        self.socket = client_socket
        self.socket_port = get_port_of_socket(self.socket)

        self.recv_from_last_value = ['']
        self.send_to_newest_value = ['']

        self.recv_from_thread = threading.Thread(target=recv_from_socket_to_pointer, args=(self.socket, self.recv_from_last_value, ))
        self.send_to_thread = threading.Thread(target=send_to_socket_from_pointer, args=(self.socket, self.send_to_newest_value, ))
        self.recv_from_thread.start()
        self.send_to_thread.start()

        self.nickname = nickname
        self.secret_key = '1234'

        self.player_game_object = Player(self.nickname, randrange(400) + 10, randrange(300) + 10, 0, connected_players_profiles=connected_players_profiles)

    def __del__(self):
        self.socket.close()


class TankGame():
    def __init__(self):
        self.join_code = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))

        self.socket = open_new_connection()
        self.connected_players = {}
        self.port = get_port_of_socket(self.socket)
        self.is_game_started = False
        self.status = "WAITING"
        self.was_two_players = False

        global AVAILABLE_GAMES
        AVAILABLE_GAMES[self.join_code] = self
    
    def check_connections(self):
        no_of_connections = 0
        for soc, player_profile in self.connected_players.items():
            if not player_profile.send_to_thread.is_alive():
                player_profile.player_game_object.health = 0
            else:
                no_of_connections += 1
        return no_of_connections
        
    # def send_no_of_connected_players(self):
    #     no_of_players = len(self.connected_players)
    #     msg = prepare_message(command='UPDATE_CHANNEL',data=no_of_players)
    #     for p in self.connected_players:
    #         p.socket.sendall()
    
    def accept_new_client(self):
        client, addr = self.socket.accept()
        print("Connected: " + addr[0] + " to game " + self.join_code)
        new_player_profile = PlayerProfil(client, self.connected_players)
        self.connected_players[client] = new_player_profile # TODO - change key from client to auth
        return new_player_profile

    def accept_new_players(self):
        while True:
            self.accept_new_client()
            self.was_two_players = True

    def wait_for_players(self):
        new_player_profile = self.accept_new_client()
        if len(self.connected_players) == 1:
            self.host_socket = new_player_profile
        
        accept_new_players_thread = threading.Thread(target=self.accept_new_players)
        accept_new_players_thread.start()
        self.accept_new_players_thread = accept_new_players_thread
        self.is_game_started = True
        self.status = "BUSY"

    def __del__(self):
        # global AVAILABLE_GAMES
        # del AVAILABLE_GAMES[self.join_code]
        # print("Delete game " + self.join_code)
        # for key, player_profile in tank_game.connected_players.items():
        #     player_profile.send_to_newest_value[0] = None

        self.socket.close()


def decode_json_data(string):
    msg = string[1]
    return json.loads(msg)


def game_loop(tank_game):
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    bullets = pygame.sprite.Group()

    tank_game.wait_for_players()
    logging.info("GAME STARTED")
    
    running = True
    while running:
        no_of_alive_connections = tank_game.check_connections()
        if no_of_alive_connections == 0:
            running = False

        players_objects = pygame.sprite.Group()
        for key, player_profile in tank_game.connected_players.items():
            players_objects.add(player_profile.player_game_object)

        for key, player_profile in tank_game.connected_players.items():
            pressed_keys = player_profile.recv_from_last_value[0]
            if pressed_keys != '':
                pressed_keys = decode_json_data(pressed_keys)
                bullets = player_profile.player_game_object.update(pressed_keys, bullets, players_objects)
            else:
                pressed_keys = pygame.key.get_pressed()
                bullets = player_profile.player_game_object.update(pressed_keys, bullets, players_objects)

        bullets.update()

        objects_positions = serialize_game_objects(players_objects, bullets)
        msg_update_game = prepare_message(command='UPDATE_GAME',status='SUCC',data=objects_positions)
        
        no_alive_players = sum([max(min(p.health, 1), 0) for p in players_objects])
        if no_alive_players == 1 and tank_game.was_two_players: 
            running = False

        for key, player_profile in tank_game.connected_players.items():
            if running == False:
                if player_profile.player_game_object.health > 0:
                    msg = prepare_message(command='GAME_OVER',status='SUCC',data=ordinal(no_alive_players))
                    player_profile.send_to_newest_value[0] = msg
                else:
                    msg = prepare_message(command='GAME_OVER',status='SUCC',data=ordinal(no_alive_players+1))
                    player_profile.send_to_newest_value[0] = msg
            else: 
                if player_profile.player_game_object.health > 0:
                    player_profile.send_to_newest_value[0] = msg_update_game
                else:
                    msg = prepare_message(command='GAME_OVER',status='SUCC',data=ordinal(no_alive_players+1))
                    player_profile.send_to_newest_value[0] = msg

        clock.tick(30)
    global AVAILABLE_GAMES
    del AVAILABLE_GAMES[tank_game.join_code]
    del tank_game


def start_the_game():
    tank_game = TankGame()
    game_threat = threading.Thread(target=game_loop, args=(tank_game, ))
    game_threat.start()
    return tank_game.join_code


def get_random_uuid_for_player():
    return str(uuid.uuid4())


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
                command = headers.get(command_header_code)

                # TODO - Check if auth and auth correct ;) 

                if command == 'REGISTER':
                    login = get_random_uuid_for_player()
                    mess = prepare_message(command='REGISTER',status='SUCC',data=login)
                    self.transport.write(mess)
                    # TODO - Zpisywanie do plaintext zarejstrowanych USSID
                    # mess = prepare_message(command='REGISTER',status='ERR')
                elif command == 'START_CHANNEL':
                    join_code = start_the_game()
                    msg = prepare_message(command='START_CHANNEL',status='SUCC', data=join_code)
                    self.transport.write(msg)
                elif command == 'JOIN_CHANNEL':
                    global AVAILABLE_GAMES
                    print(AVAILABLE_GAMES.keys())
                    join_code = headers.get('Data')
                    if join_code in AVAILABLE_GAMES:
                        mess = prepare_message(command='JOIN_CHANNEL', status='SUCC', data=str(AVAILABLE_GAMES[join_code].port)) 
                    else:
                        mess = prepare_message(command='JOIN_CHANNEL', status='ERR', data='GAME NOT EXITS') 
                    self.transport.write(mess)
                elif command == 'QUIT GAME':
                    mess = prepare_message('GAME_QUIT','SUCC','')
                    self.transport.write(mess)
                else:
                    mess = prepare_message('INVALID COMMAND','ERR','')
                    self.transport.write(mess)
            except:
                mess = prepare_message('INVALID COMMAND','ERR','')
                self.transport.write(mess)
            
    def connection_lost(self, ex):
        """ Called on client disconnect. Clean up client state """
        print('Client {} disconnected'.format(self.addr))
        clients.remove(self)


thread_pool = ThreadPoolExecutor()
loop = asyncio.get_event_loop()

# Create server and initialize on the event loop
coroutine = loop.create_server(TankGameServerProtocol, host='0.0.0.0', port=MAIN_SERVER_SOCKET_PORT)
server = loop.run_until_complete(coroutine)

# print listening socket info
for s in server.sockets:
    addr = s.getsockname()
    print('Listening on {}'.format(addr))

# Run the loop to process client connections
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
