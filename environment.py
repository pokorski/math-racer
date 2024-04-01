import os
import random

import config
from npc_car import NPCCar
from objects import (Decoration, EquationResult, OilSpill, Road, RoadBlock,
                     RoadBorder, Signpost)
from player_car import PlayerCar
from police_car import PoliceCar


class Environment:
    CLASS_MAPPING = {
        '?.?': ([(Road, {})], None),
        '?l?': ([(Road, {}), (Decoration, {'obj_type': 'left_arrow'})], None),
        '?r?': ([(Road, {}), (Decoration, {'obj_type': 'right_arrow'})], None),
        '?w?': ([(Road, {}),
                 (Decoration, {'obj_type': 'warning_road'})], None),
        '?=?': ([(Road, {}), (Decoration, {'obj_type': 'finish_line'})], None),
        'f|?': ([(RoadBorder, {'border_type': 'left'})], None),
        't|?': ([(RoadBorder, {'border_type': 'left'})], None),
        'G|?': ([(RoadBorder, {'border_type': 'left'})], None),
        'g|?': ([(RoadBorder, {'border_type': 'left'})], None),
        's|?': ([(RoadBorder, {'border_type': 'left'})], None),
        'S|?': ([(RoadBorder, {'border_type': 'left'})], None),
        'R|?': ([(RoadBorder, {'border_type': 'river_left'})], None),
        '?|f': ([(RoadBorder, {'border_type': 'right'})], None),
        '?|t': ([(RoadBorder, {'border_type': 'right'})], None),
        '?|G': ([(RoadBorder, {'border_type': 'right'})], None),
        '?|g': ([(RoadBorder, {'border_type': 'right'})], None),
        '.|s': ([(RoadBorder, {'border_type': 'right'})], None),
        '.|S': ([(RoadBorder, {'border_type': 'right'})], None),
        '.|R': ([(RoadBorder, {'border_type': 'river_right'})], None),
        'g\\.': ([(RoadBorder, {'border_type': 'left_expand'})], None),
        'g/.': ([(RoadBorder, {'border_type': 'left_shrink'})], None),
        './g': ([(RoadBorder, {'border_type': 'right_expand'})], None),
        '.\\g': ([(RoadBorder, {'border_type': 'right_shrink'})], None),
        '?g?': ([(Decoration, {'obj_type': 'grass1'})], None),
        '?G?': ([(Decoration, {'obj_type': 'grass2'})], None),
        '?R?': ([(Decoration, {'obj_type': 'river'})], None),
        '?f?': ([(Decoration, {'obj_type': 'grass1'}),
                 (Decoration, {'obj_type': 'flower'})], None),
        '?t?': ([(Decoration, {'obj_type': 'grass1'}),
                 (Decoration, {'obj_type': 'tree'})], None),
        '?s?': ([(Decoration, {'obj_type': 'grass1'}), (Signpost, {})], None),
        '?S?': ([(Decoration, {'obj_type': 'grass1'}),
                 (Decoration, {'obj_type': 'warning_sign'})], None),
        '?0?': ([(Road, {})], (NPCCar, {'npc_type': 'simple'})),
        '?1?': ([(Road, {})], (NPCCar, {'npc_type': 'nasty'})),
        '?2?': ([(Road, {})], (NPCCar, {'npc_type': 'good'})),
        '?3?': ([(Road, {})], (NPCCar, {'npc_type': 'stupid'})),
        '?p?': ([(Road, {})], (PoliceCar, {})),
        '?e?': ([(Road, {}), (EquationResult, None)], None),
        '?o?': ([(Road, {}), (OilSpill, {})], None),
        '?b?': ([(Road, {}), (RoadBlock, {})], None)
    }

    def __init__(self, level_name, equations_name):
        self.equations = self.load_equations(equations_name)
        (level_lines, self.time_extensions) = self.load_level(level_name)
        self.y_height = len(level_lines)
        self.y_pos = self.y_height - config.GAME_HEIGHT_TILES - 1.5
        self.y_goal = -1
        self.player_car = PlayerCar(self)
        self.signposts = {}
        self.initialize_objects(level_lines)
        self.y_start = self.locate_goal(1) - config.GAME_HEIGHT_TILES + 1.5
        self.player_car.position[1] = self.y_start
        self.y_goal = self.locate_goal(0)
        self.y_pos = self.y_start
        self.time_elapsed = -0.0
        self.real_time_elapsed = 0.0
        self.points = 0.0

    def load_level(self, name):
        full_name = os.path.join('levels', name)
        lines = []
        time_extensions = {}
        pos = 1
        with open(full_name, 'r') as level_file:
            for line in level_file.readlines():
                line_content = line.strip().split(' ')
                lines.append(line_content[0])
                if len(line_content) == 2:
                    time_extensions[pos] = int(line_content[1])
                pos += 1
        return (lines, time_extensions)

    def load_equations(self, name):
        full_name = os.path.join('equations', name)
        equations = []
        with open(full_name, 'r') as equations_file:
            equation_lines = equations_file.readlines()
            for i in range(0, len(equation_lines), 4):
                equations.append((
                    equation_lines[i].strip(),
                    equation_lines[i + 1].strip(),
                    equation_lines[i + 2].strip().split(',')
                ))
        return equations

    def locate_goal(self, search_type):
        rng = (0, self.y_height, +
               1) if search_type == 0 else (self.y_height - 1, -1, -1)
        for y in range(*rng):
            for x in range(0, config.GAME_WIDTH_TILES):
                for env_obj in self.env_objects[y][x]:
                    if env_obj.obj_type == 'finish_line':
                        return y

    def initialize_objects(self, level_lines):
        self.env_objects = [
            [None] * config.GAME_WIDTH_TILES for _ in range(self.y_height)]
        self.moving_objects = []
        equation_result_positions = []
        signposts = []
        for y in range(len(level_lines)):
            for x in range(len(level_lines[y])):
                matched_pattern = self.recognise_type(level_lines, x, y)
                self.env_objects[y][x] = []
                (static_args, moving_arg) = self.CLASS_MAPPING[matched_pattern]
                for static_arg in static_args:
                    (static_obj_class, static_obj_init_args) = static_arg
                    if static_obj_class == EquationResult:
                        equation_result_positions.append((x, y))
                        continue
                    obj = static_obj_class([x, y], **static_obj_init_args)
                    if static_obj_class == Signpost:
                        obj.prepare_equation(random.choice(self.equations))
                        signposts.append(obj)
                    self.env_objects[y][x].append(obj)
                if moving_arg is not None:
                    (moving_obj_class, moving_obj_init_args) = moving_arg
                    if moving_obj_class == NPCCar:
                        npc_car = NPCCar([x, y], self, **moving_obj_init_args)
                        self.moving_objects.append(npc_car)
                    if moving_obj_class == PoliceCar:
                        police_car = PoliceCar([x, y], self)
                        self.moving_objects.append(police_car)
        self.assign_equation_results(equation_result_positions, signposts)

    def assign_equation_results(self, positions, signposts):
        y_buckets = {}
        for (x, y) in positions:
            if y not in y_buckets:
                y_buckets[y] = []
            y_buckets[y].append(x)

        for y, xs in y_buckets.items():
            correct_x = random.choice(xs)
            best_signpost = None
            for signpost in signposts:
                if signpost.position[1] > y:
                    best_signpost = signpost
                    break
            assert (best_signpost is not None)

            best_signpost.answers_y = y
            for yy in range(
                    y -
                    config.GAME_HEIGHT_TILES,
                    best_signpost.position[1] -
                    config.GAME_HEIGHT_TILES):
                self.signposts[yy] = best_signpost

            incorrect_answers = random.sample(
                best_signpost.equation[2], len(xs) - 1)
            incorrect_answers_idx = 0

            correct_answer_obj = None
            for x in xs:
                value = best_signpost.equation[1]
                if x != correct_x:
                    value = incorrect_answers[incorrect_answers_idx]
                    incorrect_answers_idx += 1
                self.env_objects[y][x].append(
                    EquationResult([x, y], value, x == correct_x))
                if x == correct_x:
                    correct_answer_obj = self.env_objects[y][x][-1]
            for x in xs:
                for eo in self.env_objects[y][x]:
                    if eo.obj_type == 'equation_result':
                        eo.correct_obj = correct_answer_obj

    def safe_letter(self, level_lines, x, y):
        try:
            return level_lines[y][x]
        except BaseException:
            return 'X'

    def recognise_type(self, level_lines, x, y):
        neighbourhood_str = ''.join(
            [self.safe_letter(level_lines, x + i, y) for i in (-1, 0, 1)])
        for pattern in self.CLASS_MAPPING.keys():
            if self.match_mapping_string(pattern, neighbourhood_str):
                return pattern

        print('failure to match pattern at position (%d, %d)' % (x, y))
        print(neighbourhood_str)
        return None

    def match_mapping_string(self, pattern, text):
        for i in range(len(pattern)):
            if pattern[i] == '?':
                continue
            if pattern[i] != text[i]:
                return False
        return True

    def move(self, y_delta):
        if self.player_car.position[1] < self.y_goal:
            self.player_car.finished = True
        if self.player_car.position[1] < self.y_goal - 5.0:
            return
        if (self.time_elapsed > 1) and (
                self.time_elapsed > self.sum_time_extensions()):
            self.player_car.block()
        if not self.player_car.finished:
            self.points += (self.player_car.speed /
                            config.PLAYER_MAX_SPEED) ** 2.0
        self.y_pos -= y_delta
        if (self.player_car.started) and (not self.player_car.blocked) and (
                not self.player_car.crashed) and (
                not self.player_car.finished):
            self.time_elapsed += 1.0 / config.TARGET_FPS
        if (
            self.player_car.started) and (
            (not self.player_car.blocked) or (
                self.player_car.speed > 0)) and (
                not self.player_car.crashed) and (
                    not self.player_car.finished):
            self.real_time_elapsed += 1.0 / config.TARGET_FPS

    def get_relevant_static_objects(self, y_range=config.GAME_HEIGHT_TILES):
        IMPORTANT_TYPES = (
            'signpost',
            'warning_sign',
            'border_left_shrink',
            'border_left_expand',
            'border_right_shrink',
            'border_right_expand')

        min_y_range = max(0, int(self.y_pos - 2.5))
        max_y_range = min(int(self.y_height - 2.5),
                          int(self.y_pos + 2.5 + y_range))
        objects = []
        for y in range(min_y_range, max_y_range + 1):
            for x in range(0, config.GAME_WIDTH_TILES):
                for env_obj in self.env_objects[y][x]:
                    objects.append(env_obj)
        important_objects = [
            obj for obj in objects if obj.obj_type in IMPORTANT_TYPES]
        other_objects = [
            obj for obj in objects if obj.obj_type not in IMPORTANT_TYPES]
        return other_objects + important_objects

    def get_relevant_moving_objects(
            self, y_range=config.GAME_HEIGHT_TILES + 5):
        min_y_range = max(0, int(self.y_pos - 2.5))
        max_y_range = min(int(self.y_height - 2.5),
                          int(self.y_pos + 2.5 + y_range))
        return ([obj for obj in self.moving_objects if min_y_range <=
                 obj.position[1] <= max_y_range] + [self.player_car])

    def get_relevant_objects(self, y_range=config.GAME_HEIGHT_TILES):
        return self.get_relevant_static_objects(
            y_range) + self.get_relevant_moving_objects(y_range)

    def sum_time_extensions(self):
        return sum([delta for (pos, delta) in self.time_extensions.items(
        ) if self.player_car.position[1] <= pos])
