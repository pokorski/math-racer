import os
import sys

import pygame

import config
from sound import sound
import i18n
from i18n import trans, trans_level, trans_equations


class Menu:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 48)
        self.level_names = self.get_level_list()
        self.equations_names = self.get_equations_list()
        self.language_names = self.get_language_list()
        self.load_menu_options()
        self.key_block_frames = 0
        self.loading = False

    def get_level_list(self):
        levels_dir = os.path.join(os.path.dirname(__file__), 'levels')
        return sorted([f for f in os.listdir(levels_dir)
                       if os.path.isfile(os.path.join(levels_dir, f))])

    def get_equations_list(self):
        equations_dir = os.path.join(os.path.dirname(__file__), 'equations')
        return sorted([f for f in os.listdir(equations_dir)
                       if os.path.isfile(os.path.join(equations_dir, f))])

    def get_language_list(self):
        translations_dir = os.path.join(os.path.dirname(__file__), 'i18n')
        return sorted([os.path.splitext(os.path.basename(f))[0]
                       for f in os.listdir(translations_dir)
                       if os.path.isfile(os.path.join(translations_dir, f)) \
                       and f != '__init__.py'])


    def save_menu_options(self):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'options.txt'), 'w') as f:
            f.write(self.level_names[self.active_level_index] + '\n')
            f.write(self.equations_names[self.active_equations_index] + '\n')
            f.write('%d,%d' %
                    (config.USER_DISPLAY_MODES[self.active_resolution_index]) +
                    '\n')
            f.write('%s' %
                    (config.USER_SOUND_MODES[self.active_sound_index]) + '\n')
            f.write(self.language_names[self.active_language_index] + '\n')

    def load_menu_options(self):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'options.txt'), 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            self.active_level_index = self.level_names.index(lines[0])
            self.active_equations_index = self.equations_names.index(lines[1])
            resolution_tuple = tuple(map(int, lines[2].split(',')))
            self.active_resolution_index = config.USER_DISPLAY_MODES.index(
                resolution_tuple)
            self.active_sound_index = config.USER_SOUND_MODES.index(lines[3])
            self.active_language_index = self.language_names.index(lines[4])
            i18n.lang = self.language_names[self.active_language_index]

    def change_active_level_index(self, delta):
        index = self.active_level_index + delta
        index = min(max(0, index), len(self.level_names) - 1)
        self.active_level_index = index
        self.save_menu_options()
        self.key_block_frames = 30

    def change_active_equations_index(self, delta):
        index = self.active_equations_index + delta
        index = min(max(0, index), len(self.equations_names) - 1)
        self.active_equations_index = index
        self.save_menu_options()
        self.key_block_frames = 30

    def change_active_resolution_index(self, delta):
        index = self.active_resolution_index + delta
        index = min(max(0, index), len(config.USER_DISPLAY_MODES) - 1)
        self.active_resolution_index = index
        self.save_menu_options()
        self.key_block_frames = 30

    def change_active_sound_index(self):
        self.active_sound_index = (self.active_sound_index + 1) % 4
        self.save_menu_options()
        self.key_block_frames = 30

    def change_active_language_index(self):
        index = (self.active_language_index + 1) % len(self.language_names)
        self.active_language_index = index
        i18n.lang = self.language_names[self.active_language_index]
        self.save_menu_options()
        self.key_block_frames = 30

    def menu_frame(self, screen):
        keys = pygame.key.get_pressed()

        if self.key_block_frames == 0:
            if keys[pygame.K_LEFT]:
                self.change_active_level_index(-1)
            if keys[pygame.K_RIGHT]:
                self.change_active_level_index(+1)
            if keys[pygame.K_UP]:
                self.change_active_equations_index(-1)
            if keys[pygame.K_DOWN]:
                self.change_active_equations_index(+1)
            if keys[pygame.K_s]:
                self.change_active_sound_index()
            if keys[pygame.K_1]:
                self.change_active_resolution_index(-1)
                return ('change_window_resolution',)
            if keys[pygame.K_2]:
                self.change_active_resolution_index(+1)
                return ('change_window_resolution',)
            if keys[pygame.K_l]:
                self.change_active_language_index()
        else:
            self.key_block_frames -= 1

        self.draw(screen)

        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            self.show_loading(screen)
            sound.enabled = self.active_sound_index
            return ('play', self.level_names[self.active_level_index],
                    self.equations_names[self.active_equations_index])
        if keys[pygame.K_q]:
            pygame.quit()
            sys.exit()

    def show_loading(self, screen):
        screen.fill('black')
        screen.blit(self.font.render(trans('menu-loading'), True, 'white'),
                    (50, 50))

    def draw(self, screen):
        screen.fill('black')
        screen.blit(self.font.render('Math Racer', True, 'white'), (50, 50))
        screen.blit(self.small_font.render('Karol Pokorski - Blog o edukacji (blog.pokorski.edu.pl)', True, 'green'), (50, 100))
        screen.blit(self.font.render(
            trans('menu-level'), True, 'white'), (50, 200))
        screen.blit(self.font.render(trans_level(
            self.level_names[self.active_level_index]), True, 'yellow'),
                    (config.DISPLAY_MODE[0] * 0.5, 200))
        screen.blit(self.font.render(
            trans('menu-math-questions'), True, 'white'), (50, 300))
        screen.blit(self.font.render(trans_equations(
            self.equations_names[self.active_equations_index]), True, 'yellow'),
                    (config.DISPLAY_MODE[0] * 0.5, 300))
        screen.blit(self.font.render(
            trans('menu-window-resolution'), True, 'white'), (50, 400))
        screen.blit(
            self.font.render('%d px x %d px' % (
                config.USER_DISPLAY_MODES[self.active_resolution_index]),
                True, 'yellow'),
            (config.DISPLAY_MODE[0] * 0.5, 400))
        screen.blit(self.font.render(
            trans('menu-sound-effects'), True, 'white'), (50, 500))
        screen.blit(self.font.render(
            trans(config.USER_SOUND_MODES[self.active_sound_index]),
            True, 'yellow'),
                    (config.DISPLAY_MODE[0] * 0.5, 500))
        screen.blit(self.font.render(
            trans('menu-language'), True, 'white'), (50, 600))
        screen.blit(self.font.render(
            self.language_names[self.active_language_index], True, 'yellow'),
                    (config.DISPLAY_MODE[0] * 0.5, 600))
        screen.blit(self.font.render(
            trans('menu-start'), True, 'white'), (50, 700))
        screen.blit(self.font.render(
            trans('menu-quit'), True, 'white'), (50, 800))
