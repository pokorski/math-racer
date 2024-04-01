import random

import config
from graphics import Drawable


class PlayerCar(Drawable):
    def __init__(self, environment):
        super().__init__(
            'player_car',
            ['car.png', 'car_crashed.png', 'car_right.png', 'car_left.png'],
            0, [(config.GAME_WIDTH_TILES - 1) / 2.0, -1])
        self.speed = 0.0
        self.max_speed = 0.0
        self.crashed = False
        self.started = False
        self.finished = False
        self.blocked = False
        self.slipped_frames = 0
        self.slipped_direction = 0
        self.env_sync(environment)
        self.segments = (((25, 0), (84, 0)),
                         ((25, 108), (84, 108)),
                         ((25, 0), (25, 108)),
                         ((84, 0), (84, 108)))

    def move(self, left=False, right=False):
        if not self.started:
            return
        if self.crashed:
            return
        if self.finished:
            return
        if self.slipped_frames > 0:
            if self.slipped_direction > 0:
                self.active_sprite_index = 2
            else:
                self.active_sprite_index = 3
            self.position[0] += self.slipped_direction
            self.slipped_frames -= 1
            if self.slipped_frames == 0:
                self.active_sprite_index = 0
            return
        if left:
            self.position[0] -= config.PLAYER_HORIZ_SPEED
        if right:
            self.position[0] += config.PLAYER_HORIZ_SPEED

    def slip(self):
        if self.slipped_frames > 0:
            return
        self.slipped_frames = 35
        self.slipped_direction = \
            random.choice([-1, +1]) * (config.PLAYER_HORIZ_SPEED * 0.85) * (
                self.speed / config.PLAYER_MAX_SPEED)

    def accelerate_step(self):
        if not self.started:
            return
        if self.blocked:
            self.speed = max(0.0, self.speed - 2.5 *
                             config.PLAYER_DECEL_FACTOR)
            return
        if self.crashed:
            return
        if self.finished:
            return
        speed_ratio = self.speed / config.PLAYER_MAX_SPEED
        accel = config.PLAYER_ACCEL_FACTOR * \
            min(1.0, (1.0 + config.PLAYER_ACCEL_EASE - speed_ratio))
        self.speed = min(config.PLAYER_MAX_SPEED, self.speed + accel)

    def brake_step(self):
        if not self.started:
            return
        if self.crashed:
            return
        if self.finished:
            return
        self.speed = max(0.0, self.speed - config.PLAYER_BRAKE_FACTOR)
        if self.blocked:
            return
        self.speed = max(self.speed, min(
            self.max_speed, config.PLAYER_MIN_SPEED))

    def decelerate_step(self):
        if not self.started:
            return
        if self.blocked:
            self.speed = max(0.0, self.speed - 2.5 *
                             config.PLAYER_DECEL_FACTOR)
            return
        if self.crashed:
            return
        if self.finished:
            return
        self.speed = max(0.0, self.speed - config.PLAYER_DECEL_FACTOR)
        self.speed = max(self.speed, min(
            self.max_speed, config.PLAYER_MIN_SPEED))

    def crash(self):
        if not self.started:
            return
        if self.finished:
            return
        self.crashed = True
        self.active_sprite_index = 1
        self.speed = 0.0

    def block(self):
        self.blocked = True

    def env_sync(self, environment):
        if self.crashed:
            return
        self.max_speed = max(self.max_speed, self.speed)
        if self.finished:
            self.speed = 0.0
            self.position[1] -= config.PLAYER_WIN_SPEED
            return
        self.position[1] = environment.y_pos + config.GAME_HEIGHT_TILES - \
            0.75 - self.speed * config.PLAYER_MOVE_FACTOR
