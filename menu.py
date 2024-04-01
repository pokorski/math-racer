import os
import sys

import pygame

import config
from sound import sound


class Menu:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 72)
        self.level_names = self.get_level_list()
        self.equations_names = self.get_equations_list()
        self.load_menu_options()
        self.key_block_frames = 0
        self.loading = False

    def get_level_list(self):
        return sorted([f for f in os.listdir('levels')
                       if os.path.isfile(os.path.join('levels', f))])

    def get_equations_list(self):
        return sorted([f for f in os.listdir('equations')
                       if os.path.isfile(os.path.join('equations', f))])

    def save_menu_options(self):
        with open('options.txt', 'w') as f:
            f.write(self.level_names[self.active_level_index] + '\n')
            f.write(self.equations_names[self.active_equations_index] + '\n')
            f.write('%d,%d' %
                    (config.USER_DISPLAY_MODES[self.active_resolution_index]) +
                    '\n')
            f.write('%s' %
                    (config.USER_SOUND_MODES[self.active_sound_index]) + '\n')

    def load_menu_options(self):
        with open('options.txt', 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            self.active_level_index = self.level_names.index(lines[0])
            self.active_equations_index = self.equations_names.index(lines[1])
            resolution_tuple = tuple(map(int, lines[2].split(',')))
            self.active_resolution_index = config.USER_DISPLAY_MODES.index(
                resolution_tuple)
            self.active_sound_index = config.USER_SOUND_MODES.index(lines[3])

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
        screen.blit(self.font.render('Loading...', True, 'white'), (50, 50))

    def draw(self, screen):
        screen.fill('black')
        screen.blit(self.font.render('Math Racer', True, 'white'), (50, 50))
        screen.blit(self.font.render(
            '[Left] Level [Right] : ', True, 'white'), (50, 200))
        screen.blit(self.font.render(
            self.level_names[self.active_level_index], True, 'yellow'),
                    (config.DISPLAY_MODE[0] * 0.5, 200))
        screen.blit(self.font.render(
            '[Up] Math questions [Down] : ', True, 'white'), (50, 300))
        screen.blit(self.font.render(
            self.equations_names[self.active_equations_index], True, 'yellow'),
                    (config.DISPLAY_MODE[0] * 0.5, 300))
        screen.blit(self.font.render(
            '[1] Window resolution [2] : ', True, 'white'), (50, 400))
        screen.blit(
            self.font.render('%d px x %d px' % (
                config.USER_DISPLAY_MODES[self.active_resolution_index]),
                True, 'yellow'),
            (config.DISPLAY_MODE[0] * 0.5, 400))
        screen.blit(self.font.render(
            'Sound effects [S] : ', True, 'white'), (50, 500))
        screen.blit(self.font.render(
            config.USER_SOUND_MODES[self.active_sound_index], True, 'yellow'),
                    (config.DISPLAY_MODE[0] * 0.5, 500))
        screen.blit(self.font.render(
            '[Space] or [Enter] to start.', True, 'white'), (50, 600))
        screen.blit(self.font.render('[Q] to quit.', True, 'white'), (50, 700))
