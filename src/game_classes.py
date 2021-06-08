import pygame
import math
import random
import logging
logging.basicConfig(level=logging.INFO)

from pygame.locals import (
    RLEACCEL
)

from src.config import *


class Player(pygame.sprite.Sprite):
    def __init__(self, nickname, x, y, angle, health=DEFAULT_PLAYER_HEALTH):
        super(Player, self).__init__()
        self.health = health
        if self.health > 0:
            self.surf = pygame.image.load("media/player.png").convert()
        else:
            self.surf = pygame.image.load("media/player_dead.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(x, y)
        )
        self.speed = PLAYER_DEFAULT_SPEED
        self.angle = angle
        self.surf = pygame.transform.rotate(self.surf, angle-90)
        self.nickname = nickname
        self.font = pygame.font.SysFont("Arial", 10)
        self.textSurf = self.font.render(self.nickname, 1, pygame.Color('white'))
        self.textSurfRotated = pygame.transform.rotate(self.textSurf, 180)

        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.surf.blit(self.textSurf, [self.rect.width/2 - W/2, self.rect.height/4 - H/2]) # 
        self.surf.blit(self.textSurfRotated, [self.rect.width/2 - W/2, self.rect.height*3/4 - H/2])

    def rotate_to_angle(self, _angle):
        if _angle != self.angle:
            angle_delta = _angle - self.angle
            self.surf = pygame.transform.rotate(self.surf, angle_delta)
            self.angle = _angle

    def colide_dection_bullet(self, bullets):
        for bullet in bullets:
            if self.rect.colliderect(bullet):
                self.health = self.health - 1
                bullet.kill()
                return True
        return False

    def colide_dection_other_player(self, other_players):
        for other_player in other_players:
            if other_player.rect == self.rect:
                continue
            if self.rect.colliderect(other_player):
                return True
        return False

    def update(self, pressed_keys, bullets, other_player):
        self.colide_dection_bullet(bullets)

        if self.health < 1:
            return bullets

        if pressed_keys[K_UP]:
            self.rotate_to_angle(180)
            self.rect.move_ip(0, -self.speed)
            if self.colide_dection_other_player(other_player):
                self.rect.move_ip(0, self.speed)
        elif pressed_keys[K_DOWN]:
            self.rotate_to_angle(0)
            self.rect.move_ip(0, self.speed)
            if self.colide_dection_other_player(other_player):
                self.rect.move_ip(0, -self.speed)
        if pressed_keys[K_LEFT]:
            self.rotate_to_angle(270)
            self.rect.move_ip(-self.speed, 0)
            if self.colide_dection_other_player(other_player):
                self.rect.move_ip(self.speed, 0)
        elif pressed_keys[K_RIGHT]:
            self.rotate_to_angle(90)
            self.rect.move_ip(self.speed, 0)
            if self.colide_dection_other_player(other_player):
                self.rect.move_ip(-self.speed, 0)

        if pressed_keys[K_SPACE]:
            if self.angle == 0:
                new_Bullet = Bullet(self.rect.centerx+BULLET_FROM_PLAYER_OFFSET,self.rect.bottom-BULLET_FROM_PLAYER_OFFSET, self.angle)
            elif self.angle == 90:
                new_Bullet = Bullet(self.rect.right, self.rect.centery, self.angle)
            elif self.angle == 180:
                new_Bullet = Bullet(self.rect.centerx+BULLET_FROM_PLAYER_OFFSET, self.rect.top-BULLET_FROM_PLAYER_OFFSET, self.angle)
            elif self.angle == 270:
                new_Bullet = Bullet(self.rect.left, self.rect.centery, self.angle)
            bullets.add(new_Bullet)

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        return bullets


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super(Bullet, self).__init__()
        self.surf = pygame.image.load("media/missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(x, y)
        )
        self.speed = BULLET_DEFAULT_SPEED
        self.surf = pygame.transform.rotate(self.surf, angle+90)
        self.angle = angle

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
