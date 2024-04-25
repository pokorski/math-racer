import os

import pygame


class Sound:
    def __init__(self):
        self.samples_cache = {}
        self.enabled = 0

    def load_sample(self, name):
        if name not in self.samples_cache:
            self.samples_cache[name] = self.load_wav_mp3(name)
        return self.samples_cache[name]

    def load_wav_mp3(self, name):
        try:
            return self.load_wav(name)
        except BaseException:
            return self.load_mp3(name)

    def load_wav(self, name):
        dirname = os.path.dirname(__file__)
        full_name = os.path.join(dirname, 'sounds', name + '.wav')
        return pygame.mixer.Sound(full_name)

    def load_mp3(self, name):
        dirname = os.path.dirname(__file__)
        full_name = os.path.join(dirname, 'sounds', name + '.mp3')
        return pygame.mixer.Sound(full_name)

    def quiet(self):
        pygame.mixer.stop()

    def play(self, name):
        if (name == 'music_game') and (self.enabled < 2):
            return
        if (name != 'music_game') and (self.enabled % 2 == 0):
            return
        sound = self.load_sample(name)
        sound.play()


sound = Sound()
