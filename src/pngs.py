import pygame
from config import *
from random import randint, choice
from alarm import Alarm

class General(pygame.sprite.Sprite):
    def __init__(self, gp, pos, surface, layerZ = layers['main floor']):
        super().__init__(gp)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.layerZ = layerZ
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)


class Action(General):
    def __init__(self, gp, pos, size, name):
        surface = pygame.Surface(size)
        super().__init__(gp, pos, surface)
        self.name = name



class Water(General):
    def __init__(self, gp, pos, frames):

        # animation
        self.frames = frames
        self.current_frame = 0

        # sprite
        super().__init__(gp, pos, self.frames[self.current_frame], layers['water'])

    def animate_water(self, dt):
        self.current_frame += 5 * dt
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]

    def update(self, dt):
        self.animate_water(dt)
        super().update()

class Plants(General):
    def __init__(self, gp, pos, surface):
        super().__init__(gp, pos, surface)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)

class Trees(General):
    def __init__(self, gp, pos, surface, name, player_picks):
        super().__init__(gp, pos, surface)
        ## Cria a hitbox do tamanho total e depois reduz apenas para o toco
        self.hitbox = self.rect.copy().inflate(-40, -(self.rect.height - 48))
        self.hitbox.centery = self.rect.bottom - 24  # Ajusta para que a hitbox fique no centro do toco


        # atributos da arvore
        self.health = 5
        self.is_alive = True
        self.stump_surface = pygame.image.load('../assets/trees/stump.png').convert_alpha()
        self.timer = Alarm(200)

        # laranjas
        self.oranges_surface = pygame.image.load('../assets/fruits/orange.png')
        self.orange_pos = orange_position[name]
        self.orange_sprites = pygame.sprite.Group()
        self.add_fruit()

        self.player_picks = player_picks

        self.axe_sound = pygame.mixer.Sound('../audio/axe.wav')
        self.axe_sound.set_volume(0.1)

    def add_fruit(self):
        for pos in self.orange_pos:
            if randint(0, 10) < 2:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                General(
                    gp = [self.orange_sprites, self.groups()[0]],
                    pos = (x, y),
                    surface=self.oranges_surface,
                    layerZ=layers['fruit']
                )

    def damage_tree(self):
        self.health -= 1

        # efeito sonoro
        self.axe_sound.play()

        # cai uma laranja
        if len(self.orange_sprites.sprites()) > 0:
            random_orange = choice(self.orange_sprites.sprites())
            Effects(
                pos = random_orange.rect.topleft,
                surface = random_orange.image,
                gp = self.groups()[0],
                layer_z = layers['fruit']
            )
            self.player_picks('orange')
            random_orange.kill()

    def is_tree_dead(self):
        if self.health <= 0:
            Effects(
                pos = self.rect.topleft,
                surface = self.image,
                gp = self.groups()[0],
                layer_z = layers['fruit']
            )
            self.image = self.stump_surface
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.9)
            self.is_alive = False
            self.player_picks('wood')

    def update(self, dt):
        if self.is_alive:
            self.is_tree_dead()

class Effects(General):
    def __init__(self, pos, surface, gp, layer_z, duration=200):
        super().__init__(gp, pos, surface, layer_z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        mask_s = pygame.mask.from_surface(self.image)
        new_surface = mask_s.to_surface()
        new_surface.set_colorkey((0, 0, 0))
        self.image = new_surface

    def update(self, dt):
        ticks = pygame.time.get_ticks()
        if ticks - self.start_time > self.duration:
            self.kill()