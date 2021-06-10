import json


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
            "angle":  entity.angle,
            "health": entity.health
        }
        response_models.append(entity_temp)
    return json.dumps(response_models)


def deserialize_game_objects(msg):
    recived_objects = json.loads(msg)
    entities = []
    for recived_object in recived_objects:
        if recived_object['type'] == 'bullet':
            entity = Bullet(recived_object['centerx'], 
                            recived_object['centery'], 
                            recived_object['angle'])
            entities.append(entity)
        elif recived_object['type'] == 'player':
            entity = Player(recived_object['nickname'], 
                            recived_object['centerx'], 
                            recived_object['centery'], 
                            recived_object['angle'],
                            recived_object['health']
                            )
            entities.append(entity)
    return entities
