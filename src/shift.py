import pygame
from config import *

class Shift:
    def __init__(self, restart, player):
        self.display = pygame.display.get_surface()
        self.restart = restart
        self.player = player

        #image (blending)
        self.image = pygame.Surface((tela_largura, tela_altura))
        self.color = 255
        self.speed = -2

    def play_transition(self):
        self.color += self.speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.restart()
        if self.color > 255:
            self.color = 255
            self.player.sleeping = False
            self.speed = -2
        self.image.fill((self.color, self.color, self.color))
        self.display.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)