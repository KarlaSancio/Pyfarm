from os import walk
import pygame

def get_folder(path):
    list = []

    for _,__, files in walk(path):
        for file in files:
            complete_path = path + '/' + file
            img_surf = pygame.image.load(complete_path).convert_alpha()
            list.append(img_surf)

    return list

def get_folder_dict(path):
    dict = {}

    for _,__, files in walk(path):
        for file in files:
            complete_path = path + '/' + file
            img_surf = pygame.image.load(complete_path).convert_alpha()
            dict[file.split('.')[0]] = img_surf

    return dict