import pygame
from config import *
from alarm import Alarm

class Menu:
    def __init__(self, player, activate_menu):
        self.display = pygame.display.get_surface()
        self.player = player
        self.activate_menu = activate_menu
        self.font = pygame.font.Font('../fonts/Yana5x5.ttf', 50)

        self.width = 400
        self.space = 10
        self.padding = 8

        # menu options
        self.options = list(self.player.inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_limit = len(self.player.inventory) - 1
        self.setup()

        # andando pelo menu
        self.current_option = 0
        self.alarm = Alarm(200)

    def setup(self):
        # superficies de texto
        self.texts = []
        self.max_hight = 0
        for item in self.options:
            text = self.font.render(item, False, (0, 0, 0))
            self.texts.append(text)
            self.max_hight += text.get_height() + self.padding * 2

        self.max_hight += len(self.texts) * self.space
        self.menu_top = (tela_altura/2) - (self.max_hight/2)
        self.menu_rect = pygame.Rect((tela_largura/2) - (self.width/2), self.menu_top, self.width, self.max_hight)

        self.buy_text = self.font.render('Comprar', False, (0, 153, 0))
        self.sell_text = self.font.render('Vender', False, (179, 0, 0))

    def input(self):
        keys = pygame.key.get_pressed()
        self.alarm.update()

        if keys[pygame.K_ESCAPE]:
            self.activate_menu()

        if not self.alarm.on:
            # Movimentação do menu
            if keys[pygame.K_UP]:
                self.current_option -= 1
                self.alarm.turn_on()

            if keys[pygame.K_DOWN]:
                self.current_option += 1
                self.alarm.turn_on()

            # Ação de comprar/vender com a tecla 'SPACE'
            if keys[pygame.K_SPACE]:
                self.alarm.turn_on()
                current_item = self.options[self.current_option]

                # Verifique se o item está no inventário para vender
                if self.current_option <= self.sell_limit:
                    if self.player.inventory[current_item] > 0:
                        self.player.inventory[current_item] -= 1
                        self.player.money += price_sellable[current_item]
                else:
                    if self.player.money >= price_buyable[current_item]:
                        self.player.inventory[current_item] += 1
                        self.player.money -= price_buyable[current_item]

        # Limitar as opções
        if self.current_option < 0:
            self.current_option = len(self.options) - 1
        if self.current_option > len(self.options) - 1:
            self.current_option = 0

    def show_money(self):
        money_text = self.font.render(f'R$: {self.player.money}', False, (0, 0, 0))
        text_rect = money_text.get_rect(midbottom=(tela_largura/2, self.menu_top - 30))

        pygame.draw.rect(self.display, 'white', text_rect.inflate(20, 1), 0, border_radius=10)
        self.display.blit(money_text, text_rect)

    def show_options(self, text_surf, qtd, top, selected):

        #background
        bg_rect = pygame.Rect(self.menu_rect.left, top, self.width , text_surf.get_height() + self.padding * 2)
        pygame.draw.rect(self.display, 'white', bg_rect, 0, border_radius=10)

        #texto
        text_rect = text_surf.get_rect(midleft=(self.menu_rect.left + 20, bg_rect.centery))
        self.display.blit(text_surf, text_rect)

        # quantidade
        qtd_surf = self.font.render(str(qtd), False, (0, 0, 0))
        qtd_rect = qtd_surf.get_rect(midright=(self.menu_rect.right - 20, bg_rect.centery))
        self.display.blit(qtd_surf, qtd_rect)

        if selected:
            pygame.draw.rect(self.display, 'red', bg_rect, 5, border_radius=10)
            if self.current_option <= self.sell_limit:
                pos_rect = self.sell_text.get_rect(midleft=(self.menu_rect.left + 200, bg_rect.centery))
                self.display.blit(self.sell_text, pos_rect)
            else:
                pos_rect = self.buy_text.get_rect(midleft=(self.menu_rect.left + 200, bg_rect.centery))
                self.display.blit(self.buy_text, pos_rect)

    def update(self):
        self.input()
        self.show_money()

        for text_index, text in enumerate(self.texts):
            top = self.menu_top + (text.get_height() + (self.padding * 2) + self.space) * text_index
            qtd_list = list(self.player.inventory.values()) + list(self.player.seed_inventory.values())
            qtd = qtd_list[text_index]
            self.show_options(text, qtd, top, text_index == self.current_option)

