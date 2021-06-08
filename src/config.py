import pygame_menu

### GAME ### 
ABOUT = ['Authors: Dorota i Szymon',
         'PAS 2021']
MENU_THEME = pygame_menu.themes.THEME_DARK

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
WINDOW_SIZE = (SCREEN_HEIGHT, SCREEN_WIDTH)
USER_NAME = "ProKiller"

PLAYER_DEFAULT_SPEED = 5
BULLET_DEFAULT_SPEED = 17
BULLET_FROM_PLAYER_OFFSET = 5
DEFAULT_PLAYER_HEALTH = 5

GAME_BG = (55, 90, 55)

K_UP = 82
K_DOWN = 81
K_LEFT = 80
K_RIGHT = 79
K_SPACE = 44
K_ESCAPE = 41


### SOCKETS / NETWORK ###

SERVER_IP = 'localhost'
SERVER_NO_OF_QUEUED_CONNECTIONS = 5
MAIN_SERVER_SOCKET_PORT = 56705
RECV_BUFFOR_SIZE = 1

soft_end = '\r\n' 
hard_end = '\r\n\r\n'

command_header_code = 'Command'
status_header_code = 'Status'
lenght_header_code = 'Lenght'
auth_header_code = 'Auth'
type_of_data_header_code = 'TypeOfData'
