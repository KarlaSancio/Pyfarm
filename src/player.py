import pygame
from config import *
from aux import *
from alarm import Alarm

class Player(pygame.sprite.Sprite):
    def __init__(self, gp, pos, colliders, tree_sprites, action, soil_layer, activate_shop):
        super().__init__(gp) #chama o construtor da classe mae

        self.import_player_animations()
        self.current_animation = 'down_idle'
        self.current_frame = 0

        # setups
        self.image = self.animations[self.current_animation][self.current_frame]
        # posicionado no centro
        self.rect = self.image.get_rect(center = pos)
        self.layerZ = layers['main floor']

        # movimento do player
        self.direction = pygame.math.Vector2()
        self.posit = pygame.math.Vector2(self.rect.center)
        self.speed = 300

        # colisao
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.colliders = colliders

        # alarms
        self.alarms = {
            'tool_timer': Alarm(400, self.tool_action),
            'tool_change': Alarm(200),
            'seed_timer': Alarm(400, self.seed_action),
            'seed_change': Alarm(200)
        }
        # tools
        self.tools_list = ['axe', 'hoe', 'water']
        self.seed_index = 0
        self.chosen_tool = self.tools_list[self.seed_index]

        # crops
        self.crops = ['carrot', 'pumpkin']
        self.seed_index = 0
        self.chosen_seed = self.crops[self.seed_index]

        # inventario
        self.inventory = {
            'carrot': 0,
            'pumpkin': 0,
            'orange': 0,
            'wood': 0
        }

        self.seed_inventory = {
            'carrot': 5,
            'pumpkin': 5
        }
        self.money = 150

        # action
        self.tree_sprites = tree_sprites
        self.action = action
        self.sleeping = False
        self.soil_layer = soil_layer
        self.activte_shop = activate_shop

        # musica
        self.water_sound = pygame.mixer.Sound('../audio/water.wav')
        self.water_sound.set_volume(0.3)

    def get_target_pos(self):

        self.target_pos = self.rect.center + player_tools_offset[self.current_animation.split('_')[0]]

    # as ferramentas
    def tool_action(self):
        self.get_target_pos()
        #print('tool action')
        if self.chosen_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage_tree()
        if self.chosen_tool == 'hoe':
            self.soil_layer.get_hit_block(self.target_pos)
        if self.chosen_tool == 'water':
            self.soil_layer.water(self.target_pos)
            self.water_sound.play()



    def keysP(self):
        keys = pygame.key.get_pressed()
        if not self.alarms['tool_timer'].on and not self.sleeping:
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.current_animation = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.current_animation = 'down'
            else:
                self.direction.y = 0
            if keys[pygame.K_a]:
                self.direction.x = -1
                self.current_animation = 'left'
            elif keys[pygame.K_d]:
                self.direction.x = 1
                self.current_animation = 'right'
            else:
                self.direction.x = 0

            # usar ferramenta
            if keys[pygame.K_1]:
                # add timer
                self.alarms['tool_timer'].turn_on()
                self.direction = pygame.math.Vector2()
                self.current_frame = 0

            # trocando de ferramenta
            if keys[pygame.K_2] and not self.alarms['tool_change'].on:
                self.alarms['tool_change'].turn_on()
                self.seed_index += 1
                if self.seed_index >= len(self.tools_list):
                    self.seed_index = 0
                self.chosen_tool = self.tools_list[self.seed_index % len(self.tools_list)]

            # crops
            if keys[pygame.K_LCTRL]:
                self.alarms['seed_timer'].turn_on()
                self.direction = pygame.math.Vector2()
                self.current_frame = 0
                print('planting seed')

            # trocando de semente
            if keys[pygame.K_e] and not self.alarms['seed_change'].on:
                self.alarms['seed_change'].turn_on()
                self.seed_index += 1
                if self.seed_index >= len(self.crops):
                    self.seed_index = 0
                self.chosen_seed = self.crops[self.seed_index % len(self.crops)]
                print(self.chosen_seed)

            # checa as interacoes do player com cama e mercador
            if keys[pygame.K_RETURN]:
                collided_with_bed_sprite = pygame.sprite.spritecollide(self, self.action, False)
                if collided_with_bed_sprite:
                    if collided_with_bed_sprite[0].name == 'Merchant':
                        self.activte_shop()
                    else:
                        self.current_animation = 'left_idle'
                        self.sleeping = True

    def update(self, dt):
        self.keysP()
        self.get_player_current_animation()
        self.update_alarms()
        self.get_target_pos()
        self.animate_player(dt)
        self.player_move(dt)

    def player_move(self, dt):
        # normaliza o vetor para que o movimento seja igual em todas as direcoes
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        # movimento para vertical e horizontal
        self.posit.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.posit.x)
        self.rect.centerx = self.hitbox.centerx
        self.collide('horizontal')

        self.posit.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.posit.y)
        self.rect.centery = self.hitbox.centery
        self.collide('vertical')

    def collide(self, direction):
        for sprite in self.colliders:
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.posit.x = self.hitbox.centerx
                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.posit.y = self.hitbox.centery

    def import_player_animations(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle':[], 'down_idle':[], 'left_idle':[], 'right_idle':[],
                           'up_hoe' : [], 'down_hoe' : [], 'left_hoe' : [], 'right_hoe' : [],
                           'up_water' : [], 'down_water' : [], 'left_water' : [], 'right_water' : [],
                           'up_axe' : [], 'down_axe' : [], 'left_axe' : [], 'right_axe' : []}
        for animation in self.animations.keys():
            anim_path = '../assets/character/' + animation
            self.animations[animation] = get_folder(anim_path)
        # print(self.animations)

    def animate_player(self, dt):
        self.current_frame += 4 * dt

        if self.current_frame >= len(self.animations[self.current_animation]):
            self.current_frame = 0
        self.image = self.animations[self.current_animation][int(self.current_frame)]

    def get_player_current_animation(self):
        # idle
        # se o player estiver parado: _idle para o frame de idle
        if self.direction.magnitude() == 0:
            self.current_animation = self.current_animation.split('_')[0] + '_idle'
        if self.alarms['tool_timer'].on:
            self.current_animation = self.current_animation.split('_')[0] + '_' + self.chosen_tool


    def seed_action(self):
        if self.seed_inventory[self.chosen_seed] > 0:
            self.soil_layer.place_seed(self.chosen_seed, self.target_pos)
            self.seed_inventory[self.chosen_seed] -= 1


    def update_alarms(self):
        for alarm in self.alarms.values():
            alarm.update()
