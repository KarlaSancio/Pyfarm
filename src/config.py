from pygame.math import Vector2
#tam_tela
tela_largura = 1280
tela_altura = 720
center = (tela_largura/2, tela_altura/2)
tile_size = 64

# overlay_pos
overlay_pos ={'tools': (90, tela_altura - 5), 'crops': (40, tela_altura - 15)}

# player_tools_offset
player_tools_offset = {
    'left': Vector2(-50, 40),
    'right': Vector2(50, 40),
    'up': Vector2(0, -10),
    'down': Vector2(0, 50)
}

layers = {
    'water': 0,
    'floor': 1,
    'soil': 2,
    'soil with water': 3,
    'floor with rain': 4,
    'house bottom': 5,
    'floor plant': 6,
    'main floor': 7,
    'house top': 8,
    'fruit': 9,
    'raindrops': 10,
}

orange_position = {
    'Tree 1': [(30, 24), (60, 62), (50, 50), (70, 30), (40, 40)],
    'Tree 2': [(30, 24), (60, 62), (50, 50), (70, 30), (40, 40)]
}

grow_time = {
    'carrot': 1,
    'pumpkin': 0.5
}

price_sellable = {
    'carrot': 10,
    'pumpkin': 15,
    'orange': 5,
    'wood': 5
}

price_buyable = {
    'carrot': 20,
    'pumpkin': 30,
}

