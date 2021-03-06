import logging
from random import randrange, gauss

import pygame
from pygame.locals import (
    RLEACCEL
)

from src.config import *

logging.basicConfig(level=logging.INFO)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, health=DEFAULT_PLAYER_HEALTH, connected_players_profiles=None, nickname=' '):
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

        self.spawn_on_empty_place(connected_players_profiles)

        self.speed = PLAYER_DEFAULT_SPEED
        self.angle = angle
        self.surf = pygame.transform.rotate(self.surf, angle - 90)
        self.nickname = nickname
        self.font = pygame.font.SysFont("Arial", 10)
        self.textSurf = self.font.render(self.nickname, 1, pygame.Color('white'))
        self.textSurfRotated = pygame.transform.rotate(self.textSurf, 180)
        self.health_bar = pygame.Rect(0, 0, self.rect.width, 7)
        self.health_bar_background = pygame.Rect(0, 0, self.rect.width, 7)
        self.health_bar_background_rec = pygame.draw.rect(self.surf, (161, 161, 161), self.health_bar_background)
        self.health_bar_rec = self.draw_health_bar()

        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.surf.blit(self.textSurf, [self.rect.width / 2 - W / 2, self.rect.height / 4 - H / 2])  #
        self.surf.blit(self.textSurfRotated, [self.rect.width / 2 - W / 2, self.rect.height * 3 / 4 - H / 2])

    def spawn_on_empty_place(self, connected_players_profiles):
        if connected_players_profiles is not None:
            while True:
                is_colliding = False
                for s, other_player_profile in connected_players_profiles.items():
                    if self.rect.colliderect(other_player_profile.player_game_object.rect):
                        is_colliding = True
                if is_colliding:
                    self.rect = self.surf.get_rect(
                        center=(randrange(400) + 10, randrange(300) + 10)
                    )
                else:
                    break

    def draw_health_bar(self):
        if self.health < DEFAULT_PLAYER_HEALTH:
            r = min(255, 255 - (255 * ((self.health - (DEFAULT_PLAYER_HEALTH - self.health)) / DEFAULT_PLAYER_HEALTH)))
            g = min(255, 255 * (self.health / (DEFAULT_PLAYER_HEALTH / 2)))
            color = (r, g, 98)
            width_health = int(self.rect.width * self.health / DEFAULT_PLAYER_HEALTH)
            self.health_bar = pygame.Rect(0, 0, width_health, 7)
            return pygame.draw.rect(self.surf, color, self.health_bar)
        else:
            color = (0, 255, 98)
            self.health_bar = pygame.Rect(0, 0, self.rect.width, 7)
            return pygame.draw.rect(self.surf, color, self.health_bar)

    def rotate_to_angle(self, _angle):
        if _angle != self.angle:
            angle_delta = _angle - self.angle
            self.surf = pygame.transform.rotate(self.surf, angle_delta)
            self.angle = _angle

    def collide_detection_bullet(self, bullets):
        was_collide = False
        for bullet in bullets:
            if self.rect.colliderect(bullet):
                self.health = self.health - 1
                self.health = max(self.health, 0)
                bullet.kill()
                was_collide = True
        return was_collide

    def collide_detection_other_player(self, other_players):
        for other_player in other_players:
            if other_player.rect == self.rect:
                continue
            if self.rect.colliderect(other_player):
                return True
        return False

    def update(self, pressed_keys, bullets, other_player):
        self.collide_detection_bullet(bullets)
        if self.health < 1:
            return bullets
        self.draw_health_bar()
        self.move_player(pressed_keys, other_player)
        self.shoot(pressed_keys, bullets)
        self.keep_player_on_map()
        return bullets

    def keep_player_on_map(self):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def move_player(self, pressed_keys, other_player):
        if pressed_keys[K_UP]:
            self.rotate_to_angle(180)
            self.rect.move_ip(0, -self.speed)
            if self.collide_detection_other_player(other_player):
                self.rect.move_ip(0, self.speed)
        elif pressed_keys[K_DOWN]:
            self.rotate_to_angle(0)
            self.rect.move_ip(0, self.speed)
            if self.collide_detection_other_player(other_player):
                self.rect.move_ip(0, -self.speed)
        if pressed_keys[K_LEFT]:
            self.rotate_to_angle(270)
            self.rect.move_ip(-self.speed, 0)
            if self.collide_detection_other_player(other_player):
                self.rect.move_ip(self.speed, 0)
        elif pressed_keys[K_RIGHT]:
            self.rotate_to_angle(90)
            self.rect.move_ip(self.speed, 0)
            if self.collide_detection_other_player(other_player):
                self.rect.move_ip(-self.speed, 0)

    def shoot(self, pressed_keys, bullets):
        if pressed_keys[K_SPACE]:
            if self.angle == 0:
                new_bullet = Bullet(self.rect.centerx + BULLET_FROM_PLAYER_OFFSET,
                                    self.rect.bottom - BULLET_FROM_PLAYER_OFFSET, self.angle)
            elif self.angle == 90:
                new_bullet = Bullet(self.rect.right, self.rect.centery, self.angle)
            elif self.angle == 180:
                new_bullet = Bullet(self.rect.centerx + BULLET_FROM_PLAYER_OFFSET,
                                    self.rect.top - BULLET_FROM_PLAYER_OFFSET, self.angle)
            elif self.angle == 270:
                new_bullet = Bullet(self.rect.left, self.rect.centery, self.angle)
            bullets.add(new_bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super(Bullet, self).__init__()
        self.surf = pygame.image.load("media/missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(x, y)
        )
        self.speed = BULLET_DEFAULT_SPEED
        self.surf = pygame.transform.rotate(self.surf, angle + 90)
        self.angle = angle

    def update(self):
        self.check_is_bullet_on_map()
        self.move_bullet()

    def check_is_bullet_on_map(self):
        if self.rect.left < 0:
            self.kill()
        elif self.rect.right > SCREEN_WIDTH:
            self.kill()
        if self.rect.top <= 0:
            self.kill()
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.kill()

    def move_bullet(self):
        bullet_offset = gauss(0, BULLET_GAUSS_SIGMA)
        if self.angle == 0:
            self.rect.move_ip(bullet_offset, self.speed)
        elif self.angle == 90:
            self.rect.move_ip(self.speed, bullet_offset)
        elif self.angle == 180:
            self.rect.move_ip(bullet_offset, -self.speed)
        elif self.angle == 270:
            self.rect.move_ip(-self.speed, bullet_offset)
