import pygame
from config import *

class Overlay:
    def __init__(self, player):
        self.show_surface = pygame.display.get_surface()
        self.player = player

        # imports
        overlay_path = '../assets/overlay/'
        self.tools_dict = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools_list}
        self.crops_dict = {crop: pygame.image.load(f'{overlay_path}{crop}.png').convert_alpha() for crop in player.crops}
        print(self.tools_dict)
        print(self.crops_dict)

    def show(self):
        # show crops
        crop_surface = self.crops_dict[self.player.chosen_seed]
        crop_rect = crop_surface.get_rect(midbottom=(overlay_pos['crops']))
        self.show_surface.blit(crop_surface, crop_rect)
        # show tools
        tool_surface = self.tools_dict[self.player.chosen_tool]
        tool_rect = tool_surface.get_rect(midbottom=(overlay_pos['tools']))
        self.show_surface.blit(tool_surface, tool_rect)
