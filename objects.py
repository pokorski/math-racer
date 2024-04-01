import os
import tempfile

import matplotlib.pyplot as plt
import pygame

import config
from graphics import Drawable, invert_surface_colors


class Road(Drawable):
    def __init__(self, position):
        super().__init__('road', ['road.png'], 0, position)


class RoadBorder(Drawable):
    def __init__(self, position, border_type):
        BORDER_TYPE_INDEX = {
            'left': 0,
            'right': 1,
            'left_expand': 2,
            'left_shrink': 3,
            'right_expand': 4,
            'right_shrink': 5,
            'river_left': 6,
            'river_right': 7,
        }
        BORDER_SEGMENTS = {
            'left': (((100, 0), (100, 108)),),
            'right': (((8, 0), (8, 108)),),
            'left_expand': (((8, 8), (75, 100)), ((75, 100), (100, 100))),
            'right_expand': (((8, 100), (100, 33)), ((100, 33), (100, 8))),
            'left_shrink': (((8, 100), (8, 75)), ((8, 75), (100, 8))),
            'right_shrink': (((8, 8), (33, 8)), ((33, 8), (100, 100))),
            'river_left': (((100, 0), (100, 108)),),
            'river_right': (((8, 0), (8, 108)),)
        }

        super().__init__('border_' + border_type,
                         ['border_left.png', 'border_right.png',
                          'border_left_expand.png', 'border_left_shrink.png',
                          'border_right_expand.png', 'border_right_shrink.png',
                          'river_left.png', 'river_right.png'],
                         BORDER_TYPE_INDEX[border_type], position)
        self.segments = BORDER_SEGMENTS[border_type]

    def crash_action(self, other_object):
        if other_object.obj_type in ['player_car', 'npc_car', 'police_car']:
            other_object.crash()


class Decoration(Drawable):
    def __init__(self, position, obj_type):
        super().__init__(obj_type, [obj_type + '.png'], 0, position)


class Signpost(Drawable):
    def __init__(self, position):
        super().__init__('signpost', ['signpost.png'], 0, position)
        self.additional_drawing = self.draw_equation

    def prepare_equation(self, equation):
        self.equation = equation
        plt.clf()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        plt.text(0.5, 0.5, '$' + self.equation[0] + '$',
                 size=24, color='white', ha='center', va='center')
        plt.axis('off')
        plt.subplots_adjust(left=0.35, right=0.65, top=0.575, bottom=0.425)
        plt.savefig(temp_file.name, bbox_inches='tight',
                    pad_inches=0, transparent=True)
        self.latex_img = pygame.image.load(temp_file, temp_file.name)
        self.latex_img.set_colorkey('black')
        self.latex_img_inverted = invert_surface_colors(self.latex_img)
        os.unlink(temp_file.name)

    def draw_equation(self, screen, y_offset, override=None):
        if override is None:
            x = self.position[0] * config.TILE_WIDTH
            y = (self.position[1] - y_offset) * config.TILE_HEIGHT
        else:
            x, y = override

        screen.blit(self.latex_img_inverted,
                    (x - self.latex_img.get_width() / 2.0 - 2.0,
                     y - self.latex_img.get_height() / 2.0 - 35 - 2))
        screen.blit(self.latex_img_inverted,
                    (x - self.latex_img.get_width() / 2.0 + 2.0,
                     y - self.latex_img.get_height() / 2.0 - 35 - 2))
        screen.blit(self.latex_img_inverted,
                    (x - self.latex_img.get_width() / 2.0 - 2.0,
                     y - self.latex_img.get_height() / 2.0 - 35 + 2))
        screen.blit(self.latex_img_inverted,
                    (x - self.latex_img.get_width() / 2.0 + 2.0,
                     y - self.latex_img.get_height() / 2.0 - 35 + 2))
        screen.blit(
            self.latex_img,
            (x -
             self.latex_img.get_width() /
             2.0,
             y -
             self.latex_img.get_height() /
             2.0 -
             35))


class EquationResult(Drawable):
    def __init__(self, position, value, correct, correct_obj=None):
        super().__init__(
            'equation_result',
            ['question.png', 'question_right.png', 'question_wrong.png'],
            0, position)
        self.prepare_value(value)
        self.segments = (((20, 20), (88, 20)),
                         ((88, 20), (88, 88)),
                         ((88, 88), (20, 88)),
                         ((20, 88), (20, 20)))
        self.correct = correct
        self.correct_obj = correct_obj
        self.additional_drawing = self.draw_equation

    def prepare_value(self, value):
        self.value = value
        plt.clf()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        plt.text(0.5, 0.5, '$' + self.value + '$', size=24,
                 color='white', ha='center', va='center')
        plt.axis('off')
        plt.subplots_adjust(left=0.35, right=0.65, top=0.575, bottom=0.425)
        plt.savefig(temp_file.name, bbox_inches='tight',
                    pad_inches=0, transparent=True)
        self.latex_img = pygame.image.load(temp_file, temp_file.name)
        self.latex_img.set_colorkey('black')
        self.latex_img_inverted = invert_surface_colors(self.latex_img)
        os.unlink(temp_file.name)

    def crash_action(self, other_object):
        if other_object.obj_type == 'player_car':
            self.active_sprite_index = 1 if self.correct else 2
        if not self.correct:
            other_object.crash()
            if other_object.obj_type == 'player_car':
                self.correct_obj.active_sprite_index = 1

    def draw_equation(self, screen, y_offset):
        x = self.position[0] * config.TILE_WIDTH
        y = (self.position[1] - y_offset) * config.TILE_HEIGHT
        screen.blit(self.latex_img_inverted,
                    (x - self.latex_img.get_width() / 2 - 2.0,
                     y - self.latex_img.get_height() / 2 - 2.0))
        screen.blit(self.latex_img_inverted,
                    (x - self.latex_img.get_width() / 2 + 2.0,
                     y - self.latex_img.get_height() / 2 - 2.0))
        screen.blit(self.latex_img_inverted,
                    (x - self.latex_img.get_width() / 2 - 2.0,
                     y - self.latex_img.get_height() / 2 + 2.0))
        screen.blit(self.latex_img_inverted,
                    (x - self.latex_img.get_width() / 2 + 2.0,
                     y - self.latex_img.get_height() / 2 + 2.0))
        screen.blit(self.latex_img, (x - self.latex_img.get_width() /
                                     2, y - self.latex_img.get_height() / 2))


class OilSpill(Drawable):
    def __init__(self, position):
        super().__init__('oil_spill', ['oil_spill.png'], 0, position)
        self.segments = (((20, 20), (88, 20)),
                         ((88, 20), (88, 88)),
                         ((88, 88), (20, 88)),
                         ((20, 88), (20, 20)))

    def crash_action(self, other_object):
        if other_object.obj_type in ['player_car', 'npc_car', 'police_car']:
            other_object.slip()


class RoadBlock(Drawable):
    def __init__(self, position):
        super().__init__('road_block', ['road_block.png'], 0, position)
        self.segments = (((10, 45), (98, 45)),
                         ((98, 45), (98, 63)),
                         ((98, 63), (10, 63)),
                         ((10, 63), (10, 45)))

    def crash_action(self, other_object):
        if other_object.obj_type in ['player_car', 'npc_car', 'police_car']:
            other_object.crash()
