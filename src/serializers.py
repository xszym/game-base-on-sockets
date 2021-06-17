import json

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
)

from src.game_classes import Player, Bullet


def serialize_game_objects(players, bullets):
    response_models = []
    for entity in bullets:
        entity_temp = {
            "type": "bullet",
            "centerx": entity.rect.centerx,
            "centery": entity.rect.centery,
            "angle": entity.angle
        }
        response_models.append(entity_temp)
    for entity in players:
        entity_temp = {
            "type": "player",
            "nickname": entity.nickname,
            "centerx": entity.rect.centerx,
            "centery": entity.rect.centery,
            "angle": entity.angle,
            "health": entity.health
        }
        response_models.append(entity_temp)
    return json.dumps(response_models)


def deserialize_game_objects(msg):
    entities = []
    for recived_object in msg:
        if recived_object['type'] == 'bullet':
            entity = Bullet(recived_object['centerx'],
                            recived_object['centery'],
                            recived_object['angle'])
            entities.append(entity)
        elif recived_object['type'] == 'player':
            entity = Player(recived_object['centerx'],
                            recived_object['centery'],
                            recived_object['angle'],
                            recived_object['health'],
                            nickname=recived_object['nickname']
                            )
            entities.append(entity)
    return entities


def map_pressed_keys_to_list(pressed_keys):
    pygame_keys_ids = [K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, K_SPACE]
    result = [False] * len(pygame_keys_ids)
    for i, key_id in enumerate(pygame_keys_ids):
        result[i] = pressed_keys[key_id]
    return result
