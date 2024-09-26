import pygame
from config import *
from pytmx.util_pygame import load_pygame
from aux import *
from random import choice

class CreateSoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surface, gp):
        super().__init__(gp)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.layerZ = layers['soil']

class Plant(pygame.sprite.Sprite):
    def __init__(self, plant, gp, soil, is_watered):
        super().__init__(gp)
        self.plant = plant
        # Corrigindo o caminho para incluir a barra correta
        self.frames = get_folder(f'../assets/crops/{plant}')

        # Verifica se há frames carregados
        if not self.frames:
            raise ValueError(f"Não foram encontrados frames para a planta {plant}. Verifique o caminho e os arquivos.")

        self.soil = soil
        self.is_watered = is_watered
        self.age = 0
        self.max_age = len(self.frames) - 1  # Último estágio da planta
        self.grow_s = grow_time[plant]
        self.ready_to_harvest = False

        # Agora começamos com o primeiro frame (0) em vez do último
        self.image = self.frames[self.age]

        self.y_offset = -16 if plant == 'carrot' else -8
        self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.layerZ = layers['floor plant']

    def grow(self):
        if self.is_watered(self.rect.center):
            self.age += self.grow_s

            if int(self.age) > 0:
                self.layerZ = layers['main floor']
                self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)

            # Certifique-se de que a idade não ultrapasse o número máximo de frames
            if self.age >= self.max_age:
                self.age = self.max_age
                self.ready_to_harvest = True

            # Atualize a imagem da planta
            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))


class CreateWaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surface, gp):
        super().__init__(gp)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.layerZ = layers['soil with water']

class Soil:
    def __init__(self, every_sprite, collision_sprites):
        # groups
        self.every_sprite = every_sprite
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plants_sprites = pygame.sprite.Group()

        # soil graphics
        #self.soil_surface = pygame.image.load('../assets/soil/o.png').convert_alpha()
        self.soil_surfaces = get_folder_dict('../assets/soil')
        self.water_surfaces = get_folder('../assets/wet_soil')

        self.create_soil_cells()
        self.create_player_can_hit_blocks()

        # musica
        self.hoe_sound = pygame.mixer.Sound('../audio/hoe.wav')
        self.hoe_sound.set_volume(0.42)
        self.planting_sound = pygame.mixer.Sound('../audio/plant.wav')
        self.planting_sound.set_volume(0.1)

    def create_soil_cells(self):
        bg = pygame.image.load('../assets/farm/map1.png')
        h_tiles = bg.get_width() // tile_size
        v_tiles = bg.get_height() // tile_size

        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame('../tiled/Mapa.tmx').get_layer_by_name('Fertil').tiles():
            self.grid[y][x].append('F')

    def create_player_can_hit_blocks(self):
        self.player_can_hit_blocks = []
        for i_row, row in enumerate(self.grid):
            for i_col, cell in enumerate(row):
               if 'F' in cell:
                   x = i_col * tile_size
                   y = i_row * tile_size
                   rect = pygame.Rect(x, y, tile_size, tile_size)
                   self.player_can_hit_blocks.append(rect)

    def get_hit_block(self, point):
        for block in self.player_can_hit_blocks:
            if block.collidepoint(point):

                self.hoe_sound.play()

                x = block.x // tile_size
                y = block.y // tile_size

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_sprite()
                    if self.is_raining:
                        self.water_everything()

    def water(self, target):
        for soil_s in self.soil_sprites.sprites():
            if soil_s.rect.collidepoint(target):

                x = soil_s.rect.x // tile_size
                y = soil_s.rect.y // tile_size
                self.grid[y][x].append('W')

                pos = soil_s.rect.topleft
                surface = choice(self.water_surfaces)
                CreateWaterTile(pos, surface, [self.every_sprite, self.water_sprites])

    def water_everything(self):
        for i_row, row in enumerate(self.grid):
            for i_col, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    CreateWaterTile((i_col * tile_size, i_row * tile_size), choice(self.water_surfaces), [self.every_sprite, self.water_sprites])

    def place_seed(self, seed, target):
        for soil_s in self.soil_sprites.sprites():
            if soil_s.rect.collidepoint(target):
                self.planting_sound.play()
                x = soil_s.rect.x // tile_size
                y = soil_s.rect.y // tile_size

                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed, [self.every_sprite, self.plants_sprites, self.collision_sprites], soil_s, self.check_watered)

    def remove_water(self):
        for water_s in self.water_sprites.sprites():
            water_s.kill()

        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def create_soil_sprite(self):
        self.soil_sprites.empty()
        for i_row, row in enumerate(self.grid):
            for i_col, cell in enumerate(row):
                if 'X' in cell:
                    # auto-tiling
                    top = 'X' in self.grid[i_row - 1][i_col]
                    bottom = 'X' in self.grid[i_row + 1][i_col]
                    right = 'X' in self.grid[i_row][i_col + 1]
                    left = 'X' in self.grid[i_row][i_col - 1]

                    tile_type = 'o'

                    # todos os lados
                    if all([top, bottom, right, left]):
                        tile_type = 'x'

                    # horizontal
                    if left and not any([top, bottom, right]):
                        tile_type = 'r'
                    if right and not any([top, bottom, left]):
                        tile_type = 'l'
                    if right and left and not any([top, bottom]):
                        tile_type = 'lr'

                    # vertical
                    if top and not any([right, bottom, left]):
                        tile_type = 'b'
                    if bottom and not any([top, right, left]):
                        tile_type = 't'
                    if top and bottom and not any([right, left]):
                        tile_type = 'tb'

                    # cantos
                    if left and bottom and not any([top, right]):
                        tile_type = 'tr'
                    if right and bottom and not any([top, left]):
                        tile_type = 'tl'
                    if left and top and not any([right, bottom]):
                        tile_type = 'br'
                    if right and top and not any([left, bottom]):
                        tile_type = 'bl'

                    # 3 lados
                    if all([top, right, bottom]) and not left:
                        tile_type = 'tbr'
                    if all([top, left, bottom]) and not right:
                        tile_type = 'tbl'
                    if all([left, right, top]) and not bottom:
                        tile_type = 'lrb'
                    if all([left, right, bottom]) and not top:
                        tile_type = 'lrt'

                    CreateSoilTile((i_col * tile_size, i_row * tile_size), self.soil_surfaces[tile_type], [self.every_sprite, self.soil_sprites])

    def update_plants(self):
        for plant in self.plants_sprites.sprites():
            plant.grow()

    def check_watered(self, pos):
        x = pos[0] // tile_size
        y = pos[1] // tile_size

        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered