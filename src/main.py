import pygame, sys
from config import *
from lvl import Lvl

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((tela_largura, tela_altura))
        pygame.display.set_caption("Pyfarm")
        self.clock = pygame.time.Clock()
        self.lvl = Lvl()

    def run(self):
        # Game loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # GET DELTA TIME
            dt = self.clock.tick() / 1000
            self.lvl.run(dt)
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()