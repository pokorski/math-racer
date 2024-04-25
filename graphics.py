import os

import pygame

import config


class Graphics:
    def __init__(self):
        self.sprites_cache = {}

    def load_sprite(self, name):
        if name not in self.sprites_cache:
            self.sprites_cache[name] = self.load_png(name)
        return self.sprites_cache[name]

    def load_png(self, name):
        dirname = os.path.dirname(__file__)
        full_name = os.path.join(dirname, 'images', name)

        image = pygame.image.load(full_name)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        return image


def invert_surface_colors(surface):
    s = surface.convert_alpha()
    pixel = pygame.surfarray.pixels2d(s)
    pixel ^= 2 ** 24 - 1
    del pixel
    return s


graphics = Graphics()


class Drawable:
    def __init__(self, obj_type, filenames, default_sprite_index, position):
        self.obj_type = obj_type
        self.sprites = [graphics.load_sprite(
            filename) for filename in filenames]
        self.active_sprite_index = default_sprite_index
        self.position = position

    def draw(self, screen, y_offset, override=None):
        if override is None:
            x = self.position[0] * config.TILE_WIDTH - \
                self.sprites[self.active_sprite_index].get_width() / 2.0
            y = (self.position[1] - y_offset) * config.TILE_HEIGHT - \
                self.sprites[self.active_sprite_index].get_height() / 2.0
        else:
            x, y = override

        screen.blit(self.sprites[self.active_sprite_index], (x, y))

        if hasattr(self, 'additional_drawing'):
            self.additional_drawing(screen, y_offset)
        if not hasattr(self, 'was_painted'):
            if hasattr(self, 'first_paint_func'):
                self.first_paint_func()
            self.was_painted = True
