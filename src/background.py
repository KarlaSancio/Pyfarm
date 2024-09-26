import pygame
from config import *
from aux import get_folder
from pngs import General
from random import choice, randint

class RainDrop(General):
    def __init__(self, surf, pos, is_moving, gp, layerZ):
        super().__init__(gp, pos, surf, layerZ)

        self.duration = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        self.is_moving = is_moving
        if self.is_moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4) # efeito diagonal
            self.speed = randint(100, 150)

    def update(self, dt):
        if self.is_moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # timer
        if pygame.time.get_ticks() - self.start_time >= self.duration:
            self.kill()

class Rain:
    def __init__(self, sprites):
        self.sprites = sprites
        self.drops = get_folder('../assets/rain/drops')
        self.base = get_folder('../assets/rain/floor')
        self.base_w, self.base_h = pygame.image.load('../assets/farm/map1.png').get_size()

    def create_base(self):
        RainDrop(
            surf = choice(self.base),
            pos = (randint(0, self.base_w), randint(0, self.base_h)),
            is_moving= False,
            gp = self.sprites,
            layerZ = layers['floor with rain'])

    def create_rain_drops(self):
        RainDrop(
            surf=choice(self.drops),
            pos=(randint(0, self.base_w), randint(0, self.base_h)),
            is_moving=True,
            gp=self.sprites,
            layerZ=layers['raindrops'])

    def update(self):
        self.create_base()
        self.create_rain_drops()

class Sky:
    def __init__(self):
        self.display_surf = pygame.display.get_surface()
        self.full_surf = pygame.Surface((tela_largura, tela_altura))
        self.initial_color = [255, 255, 255]
        # azul claro
        self.final_color = [51, 133, 255]

    def draw(self, dt):
        for index, val in enumerate(self.final_color):
            if self.initial_color[index] > val:
                self.initial_color[index] -= 2 * dt
        self.full_surf.fill(self.initial_color)
        self.display_surf.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)