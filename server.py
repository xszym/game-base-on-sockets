import asyncio
import json
import logging
import random
import socket
import ssl
import string
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from random import randrange

import pygame

from src.config import *
from src.game_classes import Player
from src.serializers import serialize_game_objects
from src.utils import decode_standard_msg, recv_from_socket_to_pointer, send_to_socket_from_pointer, \
    ordinal, prepare_status_msg, prepare_game_msg, decode_game_msg, recv_msg_from_socket, decode_msg

os.environ["SDL_VIDEODRIVER"] = "dummy"
AVAILABLE_GAMES = {}
REGISTERED_CLIENTS = []
MAX_NO_GAMES = MAX_PORT - MIN_PORT
clients = []


def get_port_of_socket(sock):
    return sock.getsockname()[1]


def open_new_connection(port=0):
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

    ssock = ssl_context.wrap_socket(sock, server_side=True)
    return ssock


class PlayerProfil():
    def __init__(self, client_socket, connected_players_profiles, uuid=0):
        self.socket = client_socket
        self.socket_port = get_port_of_socket(self.socket)

        self.recv_from_last_value = ['']
        self.send_to_newest_value = ['']

        self.recv_from_thread = threading.Thread(target=recv_from_socket_to_pointer,
                                                 args=(self.socket, self.recv_from_last_value,))
        self.send_to_thread = threading.Thread(target=send_to_socket_from_pointer,
                                               args=(self.socket, self.send_to_newest_value,))
        self.recv_from_thread.start()
        self.send_to_thread.start()
        self.uuid = uuid

        self.player_game_object = Player(randrange(400) + 10, randrange(300) + 10, 0,
                                         connected_players_profiles=connected_players_profiles)

    def __del__(self):
        self.socket.close()


class TankGame():
    def __init__(self, host_uuid):
        self.join_code = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
        self.socket = open_new_connection()
        self.connected_players = {}
        self.port = get_port_of_socket(self.socket)
        self.is_game_started = False
        self.was_two_players = False
        self.host_uuid = host_uuid

        global AVAILABLE_GAMES
        AVAILABLE_GAMES[self.join_code] = self

    def check_connections(self):
        no_of_connections = 0
        for soc, player_profile in self.connected_players.items():
            if not player_profile.send_to_thread.is_alive():
                player_profile.player_game_object.health -= 0.1
                player_profile.player_game_object.health = max(player_profile.player_game_object.health, 0)
            else:
                no_of_connections += 1
        return no_of_connections

    def accept_new_client(self):
        client, addr = self.socket.accept()
        logging.info("Connected: " + addr[0] + " to game " + self.join_code)
        while True:
            recv_from_player = decode_msg(recv_msg_from_socket(client))
            if recv_from_player != '':
                nickname = recv_from_player.split(',', 1)[0]
                auth = recv_from_player.split(',', 2)[1]
                pressed_keys = recv_from_player.split(',', 2)[2]
                break

        new_player_profile = PlayerProfil(client, self.connected_players)
        if auth in self.connected_players:
            temp = self.connected_players[auth].player_game_object
            new_player_profile.player_game_object = temp
        self.connected_players[auth] = new_player_profile
        return new_player_profile

    def accept_new_players(self):
        while True:
            self.accept_new_client()
            self.was_two_players = True

    def wait_for_players(self):
        new_player_profile = self.accept_new_client()
        accept_new_players_thread = threading.Thread(target=self.accept_new_players)
        accept_new_players_thread.start()
        self.accept_new_players_thread = accept_new_players_thread
        self.is_game_started = True

    def __del__(self):
        self.socket.close()


def game_loop(tank_game):
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
            recv_from_player = player_profile.recv_from_last_value[0]
            if recv_from_player != '':
                nickname = recv_from_player.split(',', 1)[0]
                auth = recv_from_player.split(',', 2)[1]
                pressed_keys = recv_from_player.split(',', 2)[2]
                pressed_keys = decode_game_msg(pressed_keys)
                player_profile.player_game_object.nickname = nickname
                bullets = player_profile.player_game_object.update(pressed_keys, bullets, players_objects)
            else:
                pressed_keys = pygame.key.get_pressed()
                bullets = player_profile.player_game_object.update(pressed_keys, bullets, players_objects)
        bullets.update()

        objects_positions = serialize_game_objects(players_objects, bullets)
        msg_update_game = prepare_game_msg(objects_positions)

        no_alive_players = sum([max(min(p.health, 1), 0) for p in players_objects])
        if no_alive_players == 1 and tank_game.was_two_players:
            running = False

        for key, player_profile in tank_game.connected_players.items():
            if not running:
                if player_profile.player_game_object.health > 0:
                    msg = prepare_game_msg(json.dumps(['GAME_OVER', ordinal(no_alive_players)]))
                    player_profile.send_to_newest_value[0] = msg
                else:
                    msg = prepare_game_msg(json.dumps(['GAME_OVER', ordinal(no_alive_players + 1)]))
                    player_profile.send_to_newest_value[0] = msg
            else:
                if player_profile.player_game_object.health > 0:
                    player_profile.send_to_newest_value[0] = msg_update_game
                else:
                    msg = prepare_game_msg(json.dumps(['GAME_OVER', ordinal(no_alive_players + 1)]))
                    player_profile.send_to_newest_value[0] = msg
        clock.tick(30)

    global AVAILABLE_GAMES
    del AVAILABLE_GAMES[tank_game.join_code]
    del tank_game


def start_the_game(auth):
    tank_game = TankGame(auth)
    game_threat = threading.Thread(target=game_loop, args=(tank_game,))
    game_threat.start()
    return tank_game.join_code


def get_random_uuid_for_player():
    return str(uuid.uuid4())


def parse_recv_data(data):
    """ Break up raw received data into messages, delimited
        by null byte """
    parts = data.split(hard_end.encode())
    msgs = parts[:-1]
    rest = parts[-1]
    return (msgs, rest)


class MainGameServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        """ Called on instantiation, when new client connects """
        self.transport = transport
        self.addr = transport.get_extra_info('peername')
        self._rest = b''
        self.name = None
        clients.append(self)
        logging.info('Connection from {}'.format(self.addr))

    def data_received(self, data):
        """ Handle data as it's received. Broadcast complete
        messages to all other clients """
        data = self._rest + data
        (msgs, rest) = parse_recv_data(data)
        self._rest = rest

        for msg in msgs:
            try:
                global AVAILABLE_GAMES
                global REGISTERED_CLIENTS
                headers = decode_standard_msg(msg)
                command = headers.get(command_header_code)
                auth = headers.get(auth_header_code, '')
                if command == 'REGISTER':
                    new_uuid = get_random_uuid_for_player()
                    while new_uuid in REGISTERED_CLIENTS:
                        new_uuid = get_random_uuid_for_player()
                    REGISTERED_CLIENTS.append(new_uuid)
                    response_mess = prepare_status_msg(200, message='Success', data=new_uuid)
                    self.transport.write(response_mess)
                elif auth not in REGISTERED_CLIENTS:
                    mess = prepare_status_msg(400, message='Please register')
                    self.transport.write(mess)
                elif command == 'START_CHANNEL':
                    no_of_games = len(AVAILABLE_GAMES.keys())
                    if no_of_games < MAX_NO_GAMES:
                        try:
                            join_code = start_the_game(auth)
                            response_mess = prepare_status_msg(200, message='Success', data=join_code)
                        except:
                            response_mess = prepare_status_msg(400, message='Fail')
                    else:
                        response_mess = prepare_status_msg(400, message='Reached max number of games')
                    self.transport.write(response_mess)
                elif command == 'JOIN_CHANNEL':
                    join_code = headers.get(data_header_code)
                    if join_code in AVAILABLE_GAMES:
                        mess = prepare_status_msg(200, message='Success',
                                                  data=str(AVAILABLE_GAMES[join_code].port))
                    else:
                        mess = prepare_status_msg(400, message='Fail')
                    self.transport.write(mess)
                elif command == 'LIST_GAMES':
                    games = [
                        [tankgame.connected_players.get(tankgame.host_uuid, code).player_game_object.nickname, code]
                        for code, tankgame in AVAILABLE_GAMES.items()]
                    mess = prepare_status_msg(200, message='Success', data=str(list(games)))
                    self.transport.write(mess)
                else:
                    mess = prepare_status_msg(400, message='Invalid command')
                    self.transport.write(mess)
            except:
                mess = prepare_status_msg(400, message='Invalid command')
                self.transport.write(mess)

    def connection_lost(self, ex):
        """ Called on client disconnect. Clean up client state """
        logging.info('Client {} disconnected'.format(self.addr))
        clients.remove(self)


thread_pool = ThreadPoolExecutor()
loop = asyncio.get_event_loop()

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile='keys/client.crt')
ssl_context.load_cert_chain('keys/server.crt', 'keys/server.key')

coroutine = loop.create_server(MainGameServerProtocol, host='0.0.0.0', port=MAIN_SERVER_SOCKET_PORT, ssl=ssl_context)
server = loop.run_until_complete(coroutine)

for s in server.sockets:
    addr = s.getsockname()
    logging.info('Listening on {}'.format(addr))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
