import pygame

class Alarm:
    def __init__(self, time_l, func = None):

        self.time_l = time_l
        self.func = func
        self.time_s = 0
        self.on = False

    def update(self):
        ticks = pygame.time.get_ticks()
        if ticks - self.time_s >= self.time_l:
            if self.func and self.time_s != 0:
                self.func()
            self.turn_off()

    def turn_on(self):
        self.on = True
        self.time_s = pygame.time.get_ticks()

    def turn_off(self):
        self.on = False
        self.time_s = 0

