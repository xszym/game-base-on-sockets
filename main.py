# Import the pygame module
import pygame
import pygame_menu
from tkinter import *
from tkinter import messagebox
Tk().wm_withdraw() #to hide the main window

def show_popup(msg):
    messagebox.showinfo(msg,'OK')


import logging
logging.basicConfig(level=logging.INFO)

import math

# Import random for random numbers
import random

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
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

import asyncio
import websockets


ABOUT = ['Author: {0}'.format("Dorota i Szymon"),
         'PAS 2021']

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
        self.surf = pygame.image.load("player.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.angle = 90

        self.font = pygame.font.SysFont("Arial", 10)
        self.textSurf = self.font.render(name, 1, pygame.Color('white'))
        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.surf.blit(self.textSurf, [self.rect.width/2 - W/2, self.rect.height/4 - H/2]) # 
        self.surf.blit(self.textSurf, [self.rect.width/2 - W/2, self.rect.height*3/4 - H/2]) # 

    def rotate_to_angle(self, _angle):
        if _angle != self.angle:
            angle_delta = _angle - self.angle
            self.surf = pygame.transform.rotate(self.surf, angle_delta)
            self.angle = _angle
            # self.rect = self.surf.get_rect()

    # Move the sprite based on keypresses
    def update(self, pressed_keys):
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
                new_enemy = Enemy(self.rect.centerx+5,self.rect.bottom-5, self.angle)
            elif self.angle == 90:
                new_enemy = Enemy(self.rect.right, self.rect.centery, self.angle)
            elif self.angle == 180:
                new_enemy = Enemy(self.rect.centerx+5, self.rect.top-5, self.angle)
            elif self.angle == 270:
                new_enemy = Enemy(self.rect.left, self.rect.centery, self.angle)
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


# Define the enemy object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # The starting position is randomly generated, as is the speed
        self.rect = self.surf.get_rect(
            center=(
                x,
                y,
            )
        )
        self.speed = 10
        self.surf = pygame.transform.rotate(self.surf, angle+90)
        self.angle = angle

    # Move the enemy based on speed
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

        # if self.rect.right < 0:
        #     self.kill()
        # Keep player on the screen
        if self.rect.left < 0:
            self.kill()
        elif self.rect.right > SCREEN_WIDTH:
            self.kill()
        if self.rect.top <= 0:
            self.kill()
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.kill()


# Define the cloud object extending pygame.sprite.Sprite
# Use an image for a better looking sprite
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("cloud.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # The starting position is randomly generated
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    # Move the cloud based on a constant speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.right < 0:
            self.kill()


# Setup for sounds, defaults are good
# pygame.mixer.init()

# Initialize pygame
pygame.init()

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create custom events for adding a new enemy and cloud
# ADDENEMY = pygame.USEREVENT + 1
# pygame.time.set_timer(ADDENEMY, 250)
# ADDCLOUD = pygame.USEREVENT + 2
# pygame.time.set_timer(ADDCLOUD, 1000)

# Create our 'player'
player = Player(USER_NAME)

# Create groups to hold enemy sprites, cloud sprites, and all sprites
# - enemies is used for collision detection and position updates
# - clouds is used for position updates
# - all_sprites isused for rendering
enemies = pygame.sprite.Group()
clouds = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Load and play our background music
# Sound source: http://ccmixter.org/files/Apoxode/59262
# License: https://creativecommons.org/licenses/by/3.0/
# pygame.mixer.music.load("Apoxode_-_Electric_1.mp3")
# pygame.mixer.music.play(loops=-1)

# Load all our sound files
# Sound sources: Jon Fincher
# move_up_sound = pygame.mixer.Sound("Rising_putter.ogg")
# move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
# collision_sound = pygame.mixer.Sound("Collision.ogg")

# Set the base volume for all sounds
# move_up_sound.set_volume(0.5)
# move_down_sound.set_volume(0.5)
# collision_sound.set_volume(0.5)

# At this point, we're done, so we can stop and quit the mixer
# pygame.mixer.music.stop()
# pygame.mixer.quit()


def start_the_game():
    # Variable to keep our main loop running
    running = True

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

        # # Should we add a new enemy?
        # elif event.type == ADDENEMY:
        #     # Create the new enemy, and add it to our sprite groups
        #     new_enemy = Enemy()
        #     enemies.add(new_enemy)
        #     all_sprites.add(new_enemy)

        # # Should we add a new cloud?
        # elif event.type == ADDCLOUD:
        #     # Create the new cloud, and add it to our sprite groups
        #     new_cloud = Cloud()
        #     clouds.add(new_cloud)
        #     all_sprites.add(new_cloud)

        # Get the set of keys pressed and check for user input
        pressed_keys = pygame.key.get_pressed()
        print(pressed_keys)
        player.update(pressed_keys)

        # Update the position of our enemies and clouds
        enemies.update()
        clouds.update()

        # Fill the screen with sky blue
        screen.fill((135, 206, 250))

        # Draw all our sprites
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        # Check if any enemies have collided with the player
        # if pygame.sprite.spritecollideany(player, enemies):
        #     # If so, remove the player
        #     player.kill()

        #     # Stop any moving sounds and play the collision sound
        #     # move_up_sound.stop()
        #     # move_down_sound.stop()
        #     # collision_sound.play()

        #     # Stop the loop
        #     running = False

        # Flip everything to the display
        pygame.display.flip()

        # Ensure we maintain a 30 frames per second rate
        clock.tick(30)


def join_room(code):
    try:
        logging.info('TODO - próba dołączenia do  room')
    except:
        show_popup("Error")
    return


def host_game():
    start_the_game()
    # messagebox.showinfo('Continue','OK')
    return


def check_name(value):
    global USER_NAME
    USER_NAME = value


join_status = 'Insert room key'
def update_join_status(code):
    logging.debug(f'Room key {code}')
    global join_status
    if len(code) < 4:
        join_status = 'Insert room key \/'
    else:
        try:
            join_status = 'Key looking okej'
            join_room(code)
        except:
            join_status = 'Joining fail'



submenu_theme = pygame_menu.themes.THEME_DEFAULT.copy()
submenu_theme.widget_font_size = 15


# -------------------------------------------------------------------------
# Create menus:Join
# -------------------------------------------------------------------------
def draw_update_function_join_status_button(widget, menu):
    # t = widget.get_attribute('t', 0)
    # t = menu.get_clock().get_time()
    global join_status
    widget.set_title(join_status)
    # widget.set_padding(10*(1 + math.sin(t))) # Oscillating padding

join_menu = pygame_menu.Menu(
    height=WINDOW_SIZE[0],
    title='Play Menu',
    width=WINDOW_SIZE[1]
)
join_status_button = join_menu.add.button('Status: Insert code', None)
join_code_text_input = join_menu.add.text_input('Room Key: ', default='', maxchar=4, onchange=update_join_status)
# join_menu.add.button('Join room', join_room)
join_menu.add.button('Main menu', pygame_menu.events.BACK)
join_status_button.add_draw_callback(draw_update_function_join_status_button)


# -------------------------------------------------------------------------
# Create menus:About
# -------------------------------------------------------------------------
about_theme = pygame_menu.themes.THEME_DEFAULT.copy()
about_theme.widget_margin = (0, 0)

about_menu = pygame_menu.Menu(
    height=WINDOW_SIZE[0],
    theme=about_theme,
    title='About',
    width=WINDOW_SIZE[1]
)

for m in ABOUT:
    about_menu.add.label(m, align=pygame_menu.locals.ALIGN_CENTER, font_size=20)
about_menu.add.vertical_margin(30)
about_menu.add.button('Return to menu', pygame_menu.events.BACK)


main_menu = pygame_menu.Menu('PAS 2021 - CS 2D', WINDOW_SIZE[1], WINDOW_SIZE[0], theme=pygame_menu.themes.THEME_BLUE)
main_menu.add.text_input('Name: ', default=USER_NAME, maxchar=10, onchange=check_name)
main_menu.add.button('Host Game', host_game)
main_menu.add.button('Join game', join_menu)#  maxchar=4, onreturn=)
main_menu.add.button('About', about_menu)
main_menu.add.button('Quit', pygame_menu.events.EXIT)

# def draw_update_function(widget, menu):
#     # t = widget.get_attribute('t', 0)
#     # t = menu.get_clock().get_time()

#     widget.set_title("t")
#     # widget.set_padding(10*(1 + math.sin(t))) # Oscillating padding

# button = main_menu.add.button('This button updates its padding', None)
# button.add_draw_callback(draw_update_function)


if __name__ == '__main__':
    while(True):
        main_menu.mainloop(screen)