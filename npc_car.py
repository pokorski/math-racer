import random

import config
from graphics import Drawable


class NPCCar(Drawable):
    def __init__(self, position, environment, npc_type):
        super().__init__('npc_car', ['npc_car.png',
                                     'npc_car_crashed.png'], 0, position)
        self.npc_type = npc_type
        self.env = environment
        self.speed = 0.0
        self.x_shift = None
        self.smart = False
        self.crashed = False
        self.slipped_frames = 0
        self.slipped_direction = 0
        self.segments = (((40, 0), (69, 0)),
                         ((40, 108), (69, 108)),
                         ((40, 0), (40, 108)),
                         ((69, 0), (69, 108)))

    def move(self):
        if self.crashed:
            return
        self.position[1] -= self.speed
        if self.slipped_frames > 0:
            self.position[0] += self.slipped_direction
            return

        if self.x_shift is not None:
            if self.smart:
                new_x = int(self.position[0] + self.x_shift * 30 + 0.5)
                new_y = int(self.position[1] + 0.5)
                if (new_x >= 0) and (
                        new_x < config.GAME_WIDTH_TILES) and (new_y >= 0):
                    if any([hasattr(x, 'segments')
                            for x in self.env.env_objects[new_y][new_x]]):
                        return
            self.position[0] += self.x_shift
        else:
            player_dist = self.env.player_car.position[1] - self.position[1]
            if player_dist < config.NPC_DECISION_TILES:
                self.x_shift = max(-config.NPC_HORIZ_SPEED,
                                   min(config.NPC_HORIZ_SPEED,
                                       self.compute_x_shift()))

    def slip(self):
        if self.slipped_frames > 0:
            return
        self.slipped_frames = 35
        self.slipped_direction = \
            random.choice([-1, 1]) * (config.PLAYER_HORIZ_SPEED * 0.85) * (
                self.speed / config.PLAYER_MAX_SPEED)

    def compute_x_shift(self):
        if self.npc_type == 'simple':
            return 0
        if self.npc_type == 'nasty':
            x_diff = self.env.player_car.position[0] - self.position[0]
            y_diff = self.env.player_car.position[1] - self.position[1]
            self.smart = True
            return 4.0 * x_diff / y_diff / config.TARGET_FPS * \
                min(1.0, 2.0 * (self.speed / config.PLAYER_MAX_SPEED))
        if self.npc_type == 'good':
            self.smart = True
            x_diff = self.env.player_car.position[0] - self.position[0]
            if x_diff < 0.5:
                return \
                    random.choice([-1, +1]) * config.NPC_HORIZ_SPEED * \
                    min(1.0, 2.0 * (self.speed / config.PLAYER_MAX_SPEED))
            return 0
        if self.npc_type == 'stupid':
            return \
                (random.randint(-100, 100) / 80.0) * config.NPC_HORIZ_SPEED * \
                min(1.0, 2.0 * (self.speed / config.PLAYER_MAX_SPEED))

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
