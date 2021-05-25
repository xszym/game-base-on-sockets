# Import the pygame module
import pygame

# Import menu to pygame
import pygame_menu

import math
import random
import string
import asyncio
import threading
import websockets
import pickle
from time import time
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

from game_config import *
from game_classes import Player, Bullet

os.environ["SDL_VIDEODRIVER"] = "dummy"


def current_milliseconds():
	return round(time() * 1000)


##################################################33
PLAYER_INPUT = None
PLAYER_POSITIONS = None
async def serve_server(websocket, path):
    while True:
        recived_player_input = await websocket.recv()
        if recived_player_input == "None":
            pass
        elif recived_player_input is not "None":
            global PLAYER_INPUT
            PLAYER_INPUT = pickle.loads(recived_player_input)

        global PLAYER_POSITIONS
        if PLAYER_POSITIONS is not None:
            response_json = json.dumps(PLAYER_POSITIONS)
            await websocket.send(response_json)
        else:
            await websocket.send('None')


def start_loop(loop, server):
    loop.run_until_complete(server)
    loop.run_forever()


def start_player_communication_threads():
    new_loop = asyncio.new_event_loop()
    start_server = websockets.serve(
        serve_server,
        '0.0.0.0',
        int(8881),
        loop=new_loop
    )
    t = threading.Thread(target=start_loop, args=(new_loop, start_server))
    t.start()
    
start_player_communication_threads()
##################################################33

# TODO - python queue with one element
def recv_from_player_socket(_socket, _queue):
    while True:
        # TODO - data = socket.recv()
        out_q.put(data)


def send_to_player_socket(_socket, _queue):
    while True:
        data = _queue.get()
        # TODO - socket.send(data)


class PlayerProfil():
    def __init__(self, nickname):
        self.nickname = nickname
        self.secret_key = '1234'
        self.socket_port = '1234'
        self.socket = '1234'

        self.recv_from_queue = Queue()
        self.send_to_queue = Queue()

        self.recv_from_thread = threading.Thread(target=recv_from_player_socket, args=(self.socket, self.recv_from_queue, ))
        self.send_to_thread = threading.Thread(target=send_to_player_socket, args=(self.socket, self.send_to_queue, ))

        self.player_game_object = Player(self.nickname, 10, 10, 0)

        self.player_input = None
    
    def update(self):
        # TODO
        self.player_input = self.recv_from_queue.get()

    def __del__(self):
        self.recv_thread.stop()
        self.send_thread.stop()


class TankGame():
    def __init__(self):
        self.join_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        self.port = 6789
        self.connected_players = {}

    def start_game(self):
        pass

    def update(self):
        pass


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


def start_the_game():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    bullets = pygame.sprite.Group()
    players = pygame.sprite.Group()

    tank_game = TankGame()
    tank_game.connected_players['api_key'] = PlayerProfil("nickname")
    player = Player(USER_NAME, 10, 10, 0)
    players.add(player)

    running = True
    while running:
        for player in players: # tank_game.connected_players.items():
            global PLAYER_INPUT
            pressed_keys = PLAYER_INPUT
            if PLAYER_INPUT != None:
                bullets = player.update(pressed_keys, bullets)
            else:
                pressed_keys = pygame.key.get_pressed()
                bullets = player.update(pressed_keys, bullets)

        bullets.update()

        global PLAYER_POSITIONS
        PLAYER_POSITIONS = serialize_game_objects(players, bullets)

        clock.tick(30)


if __name__ == '__main__':
    game_threat = threading.Thread(target = start_the_game)
    game_threat.start()
