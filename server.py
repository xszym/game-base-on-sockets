import asyncio
import threading
import websockets
import pickle
from time import time
import os
import json
os.environ["SDL_VIDEODRIVER"] = "dummy"

def current_milliseconds():
	return round(time() * 1000)

PLAYER_INPUT = None
PLAYER_POSITIONS = None
async def serve_server(websocket, path):
    while True:
        my_pickled_object = await websocket.recv()
        if my_pickled_object == "None":
            print("None")
        else:
            global PLAYER_INPUT
            PLAYER_INPUT = pickle.loads(my_pickled_object)
            # print(PLAYER_INPUT)
        
        global PLAYER_POSITIONS
        if PLAYER_POSITIONS is not None:
            # print(pressed_keys)
            # buttons = str(pressed_keys).split("(")[1].split(")")[0]
            # print(str(pressed_keys[:10]))
            # print("Not None")
            # my_pickled_object = pickle.dumps(PLAYER_POSITIONS)
            response_json = json.dumps(PLAYER_POSITIONS)
            await websocket.send(response_json)
            # await websocket.send(str(current_milliseconds()))
        else:
            await websocket.send('None')
        delay = 30.0/1000.0
        await asyncio.sleep(delay)

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

# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()

# Import the pygame module
import pygame
import logging
logging.basicConfig(level=logging.INFO)

import math
import random

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
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

# Define constants for the screen width and height
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
WINDOW_SIZE = (SCREEN_HEIGHT, SCREEN_WIDTH)
USER_NAME = "ProKiller"


# Define the Player object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Player(pygame.sprite.Sprite):
    def __init__(self, name):
        super(Player, self).__init__()
        self.surf = pygame.image.load("media/player.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.angle = 90
        self.nickname = name

        self.font = pygame.font.SysFont("Arial", 10)
        self.textSurf = self.font.render(self.nickname, 1, pygame.Color('white'))
        self.textSurfRotated = pygame.transform.rotate(self.textSurf, 180)

        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.surf.blit(self.textSurf, [self.rect.width/2 - W/2, self.rect.height/4 - H/2]) # 
        self.surf.blit(self.textSurfRotated, [self.rect.width/2 - W/2, self.rect.height*3/4 - H/2]) # 

    def rotate_to_angle(self, _angle):
        if _angle != self.angle:
            angle_delta = _angle - self.angle
            self.surf = pygame.transform.rotate(self.surf, angle_delta)
            self.angle = _angle

    # Move the sprite based on keypresses
    def update(self, pressed_keys, bullets):
        if pressed_keys[K_UP]:
            self.rotate_to_angle(180)
            self.rect.move_ip(0, -5)
        elif pressed_keys[K_DOWN]:
            self.rotate_to_angle(0)
            self.rect.move_ip(0, 5)
        elif pressed_keys[K_LEFT]:
            self.rotate_to_angle(270)
            self.rect.move_ip(-5, 0)
        elif pressed_keys[K_RIGHT]:
            self.rotate_to_angle(90)
            self.rect.move_ip(5, 0)

        if pressed_keys[K_SPACE]:
            if self.angle == 0:
                new_Bullet = Bullet(self.rect.centerx+5,self.rect.bottom-5, self.angle)
            elif self.angle == 90:
                new_Bullet = Bullet(self.rect.right, self.rect.centery, self.angle)
            elif self.angle == 180:
                new_Bullet = Bullet(self.rect.centerx+5, self.rect.top-5, self.angle)
            elif self.angle == 270:
                new_Bullet = Bullet(self.rect.left, self.rect.centery, self.angle)
            bullets.add(new_Bullet)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        return bullets

# Define the Bullet object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super(Bullet, self).__init__()
        self.surf = pygame.image.load("media/missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # The starting position is randomly generated, as is the speed
        self.rect = self.surf.get_rect(
            center=(
                x,
                y,
            )
        )
        self.speed = 17
        self.surf = pygame.transform.rotate(self.surf, angle+90)
        self.angle = angle

    # Move the Bullet based on speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        if self.angle == 0:
            self.rect.move_ip(0, self.speed)
        elif self.angle == 90:
            self.rect.move_ip(self.speed, 0)
        elif self.angle == 180:
            self.rect.move_ip(0, -self.speed)
        elif self.angle == 270:
            self.rect.move_ip(-self.speed, 0)

        if self.rect.left < 0:
            self.kill()
        elif self.rect.right > SCREEN_WIDTH:
            self.kill()
        if self.rect.top <= 0:
            self.kill()
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.kill()


def start_the_game():
    # Variable to keep our main loop running
    running = True
    # Initialize pygame
    pygame.init()

    # Setup the clock for a decent framerate
    clock = pygame.time.Clock()

    # Create the screen object
    # The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Create our 'player'
    player = Player(USER_NAME)
    
    bullets = pygame.sprite.Group()
    players = pygame.sprite.Group()
    players.add(player)

    # Our main loop
    while running:
    # Look at every event in the queue
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop
                if event.key == K_ESCAPE:
                    running = False

            # Did the user click the window close button? If so, stop the loop
            elif event.type == QUIT:
                running = False

        # Get the set of keys pressed and check for user input
        for player in players:
            global PLAYER_INPUT
            pressed_keys = PLAYER_INPUT
            if PLAYER_INPUT != None:
                print("Input from server")
                # print(pressed_keys)
                bullets = player.update(pressed_keys, bullets)
            else:
                pressed_keys = pygame.key.get_pressed()
                bullets = player.update(pressed_keys, bullets)

        # Update the position of our bullets and clouds
        bullets.update()
        # players.update()

        # # Draw all our sprites
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

        global PLAYER_POSITIONS
        PLAYER_POSITIONS = response_models
        # Check if any bullets have collided with the player
        # if pygame.sprite.spritecollideany(player, bullets):
        #     # If so, remove the player
        #     player.kill()

        #     # Stop the loop
        #     running = False

        # Flip everything to the display
        # pygame.display.flip()

        # Ensure we maintain a 30 frames per second rate
        clock.tick(30)


if __name__ == '__main__':
    start_the_game()
