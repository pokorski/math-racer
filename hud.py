import pygame

import config
from i18n import trans, trans_level, trans_equations


class HUD:
    def __init__(self):
        self.game_size = ((config.GAME_WIDTH_TILES - 1) * config.TILE_WIDTH,
                          config.DISPLAY_MODE[1])
        self.screen_size = (
            config.DISPLAY_MODE[0]
            - (config.GAME_WIDTH_TILES - 1) * config.TILE_WIDTH,
            config.DISPLAY_MODE[1])
        self.screen_position = (
            (config.GAME_WIDTH_TILES - 1) * config.TILE_WIDTH, 0)
        self.surface = pygame.Surface(self.screen_size)
        self.surface.fill('black')
        self.small_font = pygame.font.SysFont(None, 48)
        self.font = pygame.font.SysFont(None, 72)
        self.big_font = pygame.font.SysFont(None, 144)

    def display(self, screen, text):
        text_surface_black = self.big_font.render(text, True, 'black')
        screen.blit(text_surface_black, ((
            self.game_size[0] - text_surface_black.get_width()) / 2.0, 100))
        text_surface_white = self.big_font.render(text, True, 'white')
        screen.blit(
            text_surface_white,
            ((self.game_size[0] - text_surface_white.get_width()) / 2.0 - 2,
             100 - 2))

    def draw(self, screen, speed, pos, pos_start, pos_goal,
             points, time_left, time_passed,
             signposts,
             car_position,
             level_name, equations_name):
        speed_percent = speed / config.PLAYER_MAX_SPEED
        hud_speed = config.HUD_MAX_SPEED * speed_percent
        hud_position = min(100.0, max(
            0.0, (pos - pos_start) / (pos_goal - pos_start) * 100.0))
        hud_points = int(points)
        hud_time_left = int(time_left)

        self.surface.fill('black')

        self.surface.blit(self.small_font.render(
            trans_level(level_name), True, 'white'), (50, 50))
        self.surface.blit(self.small_font.render(
            trans_equations(equations_name), True, 'white'), (50, 100))

        self.surface.blit(self.font.render(
            trans('hud-speed'), True, 'white'), (50, 400))
        speed_surface = self.font.render(
            '%.0f km/h' % (hud_speed), True, 'yellow')
        self.surface.blit(
            speed_surface,
            (self.surface.get_width() - speed_surface.get_width() - 50, 400))

        self.surface.blit(self.font.render(
            trans('hud-progress'), True, 'white'), (50, 500))
        position_surface = self.font.render(
            '%.0f %%' % (hud_position), True, 'yellow')
        self.surface.blit(
            position_surface,
            (self.surface.get_width() -
             position_surface.get_width() -
             50,
             500))

        self.surface.blit(self.font.render(
            trans('hud-time-left'), True, 'white'), (50, 700))
        speed_surface = self.font.render(
            '%d s' % (hud_time_left), True, 'yellow')
        self.surface.blit(
            speed_surface,
            (self.surface.get_width() -
             speed_surface.get_width() -
             50,
             700))

        speed_progress_bar = pygame.Surface((self.screen_size[0] - 100, 20))
        speed_progress_bar.fill('white')
        speed_progress_bar_filled = pygame.Surface(
            (int((self.screen_size[0] - 102) * speed_percent), 18))
        speed_progress_bar_filled.fill('red')
        speed_progress_bar.blit(speed_progress_bar_filled, (1, 1))
        self.surface.blit(speed_progress_bar, (50, 450))

        position_progress_bar = pygame.Surface((self.screen_size[0] - 100, 20))
        position_progress_bar.fill('white')
        position_progress_bar_filled = pygame.Surface(
            (int((self.screen_size[0] - 102) * hud_position / 100.0), 18))
        position_progress_bar_filled.fill('red')
        position_progress_bar.blit(position_progress_bar_filled, (1, 1))
        self.surface.blit(position_progress_bar, (50, 550))

        self.surface.blit(self.font.render(
            trans('hud-score'), True, 'white'), (50, self.surface.get_height() - 150))
        points_surface = self.font.render('%d' % (hud_points), True, 'yellow')
        self.surface.blit(
            points_surface,
            (self.surface.get_width() -
             points_surface.get_width() -
             50,
             self.surface.get_height() -
             150))

        self.surface.blit(
            self.font.render(trans('hud-time-elapsed'), True, 'white'),
            (50, self.surface.get_height() - 250))
        time_surface = self.font.render(
            '%.2f s' % (max(0, time_passed)), True, 'yellow')
        self.surface.blit(
            time_surface,
            (self.surface.get_width() - time_surface.get_width() - 50,
             self.surface.get_height() - 250))

        y = int(pos)
        if y in signposts:
            signposts[y].draw(self.surface, pos, (100, 200))
            signposts[y].draw_equation(
                self.surface,
                pos,
                (100 + config.TILE_WIDTH,
                 200 + config.TILE_HEIGHT / 2 + 15))

            signpost_diff = signposts[y].position[1] - signposts[y].answers_y
            pos_diff = car_position - signposts[y].answers_y
            pos_elapsed = max(0, signpost_diff - pos_diff)

            signpost_progress_bar = pygame.Surface((202, 10))
            signpost_progress_bar.fill('white')
            signpost_progress_bar_filled = pygame.Surface(
                (int((pos_elapsed / signpost_diff) * 200.0), 8))
            signpost_progress_bar_filled.fill('red')
            signpost_progress_bar.blit(signpost_progress_bar_filled, (1, 1))
            self.surface.blit(signpost_progress_bar, (110, 260))

        screen.blit(self.surface, self.screen_position)
