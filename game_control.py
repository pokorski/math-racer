import pygame

import config
import environment
import hud
import menu
from collisions import check_object_collision
from sound import sound
from i18n import trans


class GameControl:
    def __init__(self):
        self.initialize_menu()
        self.initialize_window()

    def initialize_window(self):
        self.window_resolution = \
            config.USER_DISPLAY_MODES[self.menu.active_resolution_index]
        self.actual_screen = pygame.display.set_mode(self.window_resolution)
        self.screen = pygame.Surface(config.DISPLAY_MODE)

    def frame(self):
        if self.mode == 'menu':
            self.menu_frame()
        if self.mode == 'game':
            self.game_frame()
        self.refresh()

    def refresh(self, force=False):
        frame = pygame.transform.scale(self.screen, self.window_resolution)
        self.actual_screen.blit(frame, (0, 0))
        if force:
            pygame.display.flip()

    def initialize_menu(self):
        self.mode = 'menu'
        sound.quiet()
        self.menu = menu.Menu()

    def menu_frame(self):
        menu_return = self.menu.menu_frame(self.screen)
        if menu_return is None:
            return
        if menu_return[0] == 'play':
            self.refresh(force=True)
            self.initialize_game(*menu_return[1:])
        if menu_return[0] == 'change_window_resolution':
            self.initialize_window()
            self.initialize_menu()

    def initialize_game(self, level_name, equations_name):
        self.level_name, self.equations_name = level_name, equations_name
        self.env = environment.Environment(level_name, equations_name)
        self.hud = hud.HUD()
        self.started_frames = 0
        self.finished_frames = 0
        self.restart = False

        self.mode = 'game'

        sound.quiet()
        sound.play('music_game')
        sound.play('start')

        self.prev_time_left = None
        self.time_extended_frames = 0

    def game_frame(self):
        keys = pygame.key.get_pressed()

        self.env.player_car.move(
            keys[pygame.K_LEFT], keys[pygame.K_RIGHT])
        if (keys[pygame.K_UP] or keys[pygame.K_LCTRL]) and (
                keys[pygame.K_DOWN] or keys[pygame.K_LALT]):
            self.env.player_car.decelerate_step()
        elif keys[pygame.K_UP] or keys[pygame.K_LCTRL]:
            self.env.player_car.accelerate_step()
        elif keys[pygame.K_DOWN] or keys[pygame.K_LALT]:
            self.env.player_car.brake_step()
        else:
            self.env.player_car.decelerate_step()

        if keys[pygame.K_ESCAPE]:
            self.initialize_menu()
            return

        self.env.move(self.env.player_car.speed)
        self.env.player_car.env_sync(self.env)

        objects = self.env.get_relevant_objects()
        moving_objects = self.env.get_relevant_moving_objects()

        for obj in moving_objects:
            obj.move()

        for obj1 in moving_objects:
            if obj1.obj_type == 'police_car':
                if 1 <= obj1.position[1] \
                        - self.env.player_car.position[1] <= 6:
                    if self.env.player_car.speed - obj1.speed > \
                            config.PLAYER_MAX_SPEED * \
                            config.POLICE_SPEED_DIFF_ALERT_FACTOR + \
                            config.POLICE_SPEED_DIFF_ALERT_ADDIT:
                        obj1.alert_start()

            for obj2 in objects:
                if obj1 == obj2:
                    continue
                if obj2.obj_type == 'player_car':
                    continue
                if check_object_collision(obj1, obj2):
                    obj2.crash_action(obj1)

        for obj in objects:
            obj.draw(self.screen, self.env.y_pos)

        time_left = self.env.sum_time_extensions() - self.env.time_elapsed

        self.hud.draw(self.screen,
                      self.env.player_car.speed,
                      self.env.y_pos,
                      self.env.y_start,
                      self.env.y_goal,
                      self.env.points,
                      time_left,
                      self.env.real_time_elapsed,
                      self.env.signposts,
                      self.env.player_car.position[1],
                      self.level_name,
                      self.equations_name)

        self.started_frames += 1

        if self.started_frames <= 1 * config.TARGET_FPS:
            self.hud.display(self.screen, '3')
        elif self.started_frames <= 2 * config.TARGET_FPS:
            self.hud.display(self.screen, '2')
        elif self.started_frames <= 3 * config.TARGET_FPS:
            self.hud.display(self.screen, '1')
        elif self.started_frames <= 5 * config.TARGET_FPS:
            self.hud.display(self.screen, 'GO!')

        if self.started_frames >= 3 * config.TARGET_FPS:
            self.env.player_car.started = True

        if self.env.player_car.finished:
            if self.finished_frames == 0:
                sound.quiet()
                sound.play('congratulations')
            self.finished_frames += 1
            self.hud.display(self.screen, trans('congratulations'))
        elif self.env.player_car.crashed:
            if self.finished_frames == 0:
                sound.quiet()
                sound.play('fail')
            self.finished_frames += 1
            self.hud.display(self.screen, trans('crashed'))
            self.restart = True
        elif self.env.player_car.blocked and \
                self.env.player_car.speed < 0.00001:
            if self.finished_frames == 0:
                sound.quiet()
                sound.play('fail')
            self.finished_frames += 1
            self.hud.display(self.screen, trans('time-up'))
            self.restart = True
        else:
            if ((self.prev_time_left is not None) and
                (time_left > self.prev_time_left)) or \
                    (1 <= self.time_extended_frames <= 3 * config.TARGET_FPS):
                if self.time_extended_frames == 0:
                    sound.play('checkpoint')
                    self.env.player_car.blocked = False

                if self.time_extended_frames <= 0.33 * config.TARGET_FPS:
                    self.hud.display(self.screen, trans('time-extended'))
                elif self.time_extended_frames <= 0.67 * config.TARGET_FPS:
                    pass
                elif self.time_extended_frames <= 1 * config.TARGET_FPS:
                    self.hud.display(self.screen, trans('time-extended'))
                elif self.time_extended_frames <= 1.33 * config.TARGET_FPS:
                    pass
                elif self.time_extended_frames <= 1.67 * config.TARGET_FPS:
                    self.hud.display(self.screen, trans('time-extended'))
                elif self.time_extended_frames <= 2 * config.TARGET_FPS:
                    pass
                elif self.time_extended_frames <= 3 * config.TARGET_FPS:
                    self.hud.display(self.screen, trans('time-extended'))
                self.time_extended_frames += 1
            else:
                self.time_extended_frames = 0

            if ((time_left <= 0) and (self.prev_time_left > 0)):
                sound.play('end_beep')
            elif (int(time_left) <= 10) and \
                 (int(time_left) < int(self.prev_time_left)):
                sound.play('beep')

            self.prev_time_left = time_left

        if self.finished_frames >= 1 * config.TARGET_FPS and self.restart:
            self.initialize_game(self.level_name, self.equations_name)
        if self.finished_frames >= 5 * config.TARGET_FPS:
            if not self.restart:
                self.initialize_menu()
