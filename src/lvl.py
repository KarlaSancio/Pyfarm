import pygame, sys
from config import *
from player import Player
from overlay import Overlay
from pngs import General, Water, Plants, Trees, Action, Effects
from pytmx.util_pygame import load_pygame
from aux import *
from shift import Shift
from soil import Soil
from background import Sky, Rain
from random import randint
from menu import Menu

class Lvl:
    def __init__(self):
        self.show_surface = pygame.display.get_surface()

        #groups
        self.assets = Camera()
        self.colliders = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.action = pygame.sprite.Group()

        self.soil_layer = Soil(self.assets, self.colliders)
        self.add_setup()
        self.overlay = Overlay(self.player)
        self.shift = Shift(self.restart_day, self.player)

        # chuva
        self.rain = Rain(self.assets)
        self.is_raining = randint(0, 8) > 5
        self.soil_layer.is_raining = self.is_raining
        self.sky = Sky()

        # loja
        self.menu = Menu(self.player, self.activate_shop)
        self.shop_active = False

        # sound
        self.succes_sound = pygame.mixer.Sound('../audio/Success1.wav')
        self.succes_sound.set_volume(0.1)
        self.music = pygame.mixer.Sound('../audio/theme.ogg')
        self.music.play(loops=-1)
        self.music.set_volume(0.2)


    def add_setup(self):
        tmx_info = load_pygame('../tiled/Mapa.tmx')
        #object_layer = tmx_info.get_layer_by_name('Objetos')

        # house
        for layer in ['House Floor']:
            for x, y, surf in tmx_info.get_layer_by_name(layer).tiles():
                General(self.assets, (x * tile_size, y * tile_size), surf, layers['house bottom'])

        # furniture
        for layer in ['House Furniture', 'House Walls', 'House Walls Top']:
            for x, y, surf in tmx_info.get_layer_by_name(layer).tiles():
                General(self.assets, (x * tile_size, y * tile_size), surf)

        # fence
        for layer in ['Fence']:
            for x, y, surf in tmx_info.get_layer_by_name(layer).tiles():
                General([self.assets, self.colliders], (x * tile_size, y * tile_size), surf)

        # player
        for obj in tmx_info.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    gp = self.assets,
                    pos = (obj.x, obj.y),
                    colliders = self.colliders,
                    tree_sprites = self.tree_sprites,
                    action = self.action,
                    soil_layer = self.soil_layer,
                    activate_shop = self.activate_shop)

            if obj.name == 'Cama1':
                Action(self.action, (obj.x, obj.y), (obj.width, obj.height), obj.name)

            if obj.name == 'Merchant':
                Action(self.action, (obj.x, obj.y), (obj.width, obj.height), obj.name)

        General(pos = (0, 0),
                surface = pygame.image.load('../assets/farm/map1.png').convert_alpha(),
                gp = self.assets,
                layerZ = layers['floor'])

        # Water
        water_frames = get_folder('../assets/water')
        for x, y, surf in tmx_info.get_layer_by_name('Agua').tiles():
            Water(self.assets, (x * tile_size, y * tile_size), water_frames)

        # Plants
        for obj in tmx_info.get_layer_by_name('PlantasObj'):
            Plants([self.assets, self.colliders], (obj.x, obj.y), obj.image)

        # Trees
        for obj in tmx_info.get_layer_by_name('Arvores'):
            Trees(
                gp = [self.assets, self.colliders, self.tree_sprites],
                pos = (obj.x, obj.y),
                surface= obj.image,
                name=obj.name,
                player_picks = self.player_pickup
            )

        # Colliders
        for obj in tmx_info.get_layer_by_name('Colisores').tiles():
            General(self.colliders, (obj[0] * tile_size, obj[1] * tile_size), obj[2])

    def activate_shop(self):
        self.shop_active = not self.shop_active


    def run(self, dt):
        # Game loop
        self.show_surface.fill((0, 0, 0))
        self.assets.custom_draw(self.player)

        if self.shop_active:
            self.menu.update()
        else:
            self.assets.update(dt)
            self.plant_collider()

        self.overlay.show()

        # chuva
        if self.is_raining and not self.shop_active:
            self.rain.update()

        # checa se o player esta dormindo
        if self.player.sleeping:
            self.shift.play_transition()

        # ceu
        self.sky.draw(dt)
        #print(self.player.inventory)


    def restart_day(self):
        # plants
        self.soil_layer.update_plants()


        self.soil_layer.remove_water()
        self.is_raining = randint(0, 8) > 5
        self.soil_layer.raining = self.is_raining
        if self.is_raining:
            self.soil_layer.water_everything()

        # reseta as laranjas das arvores
        for tree in self.tree_sprites.sprites():
            for orange in tree.orange_sprites.sprites():
                orange.kill()
            tree.add_fruit()

        # resetando o ceu
        self.sky.initial_color = [255, 255, 255]

    def plant_collider(self):
        if self.soil_layer.plants_sprites:
            for plant in self.soil_layer.plants_sprites.sprites():
                if plant.ready_to_harvest and plant.rect.colliderect(self.player.hitbox):
                    self.player_pickup(plant.plant)
                    plant.kill()
                    Effects(plant.rect.topleft, plant.image, self.assets, layers['main floor'])
                    self.soil_layer.grid[plant.rect.centery // tile_size][plant.rect.centerx // tile_size].remove('P')


    def player_pickup(self, item):
        self.player.inventory[item] += 1
        self.succes_sound.play()

class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.show_surface = pygame.display.get_surface()
        self.camera = pygame.math.Vector2()

    def custom_draw(self, player):
        self.camera.x = player.rect.centerx - tela_largura/2
        self.camera.y = player.rect.centery - tela_altura/2

        for layer in layers.values():
            for sprite in sorted(self.sprites(), key=lambda x: x.rect.centery):
                if sprite.layerZ == layer:
                    camera_rect = sprite.rect.copy()
                    camera_rect.center -= self.camera
                    self.show_surface.blit(sprite.image, camera_rect)

                    #debug hitbox tool
                    #if sprite == player:
                        #pygame.draw.rect(self.show_surface, 'red', camera_rect, 5)
                        #hitbox_rect = player.hitbox.copy()
                        #hitbox_rect.center = camera_rect.center
                        #pygame.draw.rect(self.show_surface, 'green', hitbox_rect, 5)
                        #target_pos = camera_rect.center + player_tools_offset[player.current_animation.split('_')[0]]
                        #pygame.draw.circle(self.show_surface, 'blue', target_pos, 5)
