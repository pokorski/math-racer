import random

import config
from graphics import Drawable
from sound import sound


class PoliceCar(Drawable):
    def __init__(self, position, environment):
        super().__init__('police_car',
                         ['police.png',
                          'police_crashed.png',
                          'police_alert1.png',
                          'police_alert2.png'],
                         0,
                         position)
        self.env = environment
        self.speed = 0.0
        self.crashed = False
        self.slipped_frames = 0
        self.slipped_direction = 0
        self.x_shift = 0
        self.alert = False
        self.alert_speed = False
        self.alert_frames = 0
        self.segments = (((40, 0), (69, 0)),
                         ((40, 108), (69, 108)),
                         ((40, 0), (40, 108)),
                         ((69, 0), (69, 108)))

    def move(self):
        if self.crashed:
            return
        if self.alert:
            self.active_sprite_index = 2 + (self.alert_frames % 20) // 10
            self.alert_frames += 1
            self.x_shift = \
                max(-config.NPC_HORIZ_SPEED,
                    min(config.NPC_HORIZ_SPEED,
                        self.env.player_car.position[0] - self.position[0]))
            self.speed = min(self.speed + config.POLICE_DELTA_ACCEL_FACTOR,
                             self.alert_speed + config.PLAYER_MAX_SPEED / 3.0)
        if self.slipped_frames > 0:
            self.position[0] += self.slipped_direction
            return
        self.position[1] -= self.speed
        if self.x_shift is not None:
            new_x = int(self.position[0] + self.x_shift * 30 + 0.5)
            new_y = int(self.position[1] + 0.5)
            if (0 <= new_x < config.GAME_WIDTH_TILES) and (new_y >= 0):
                if any([hasattr(x, 'segments')
                        for x in self.env.env_objects[new_y][new_x]]):
                    return
            self.position[0] += self.x_shift

    def slip(self):
        if self.slipped_frames > 0:
            return
        self.slipped_frames = 35
        self.slipped_direction = \
            random.choice([-1, 1]) * (config.PLAYER_HORIZ_SPEED * 0.85) * (
                self.speed / config.PLAYER_MAX_SPEED)

    def alert_start(self):
        if self.alert:
            return
        if self.crashed:
            return
        self.alert = True
        self.alert_speed = self.speed
        self.speed *= 1.1
        sound.play('police')

    def crash_action(self, other_object):
        self.crash()
        if hasattr(other_object, 'crash'):
            other_object.crash()

    def crash(self):
        self.crashed = True
        self.active_sprite_index = 1
        self.speed = 0.0

    def first_paint_func(self):
        self.speed = (self.env.player_car.speed *
                      (90 + random.randint(0, 20)) / 100.0) / 2.0
