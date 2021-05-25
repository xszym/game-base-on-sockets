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


new_loop = asyncio.new_event_loop()
start_server = websockets.serve(
	serve_server,
	'0.0.0.0',
	int(8881),
    loop=new_loop
)

def start_loop(loop, server):
    loop.run_until_complete(server)
    loop.run_forever()

t = threading.Thread(target=start_loop, args=(new_loop, start_server))
t.start()


class TankGame():
    def __init__(self):
        self.join_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        self.port = 6789

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

    player = Player(USER_NAME, 10, 10, 0)
    players.add(player)

    running = True
    while running:
        for player in players:
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
    # start_the_game()
