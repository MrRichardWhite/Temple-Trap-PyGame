# ---------------------------------------------------------------- #

import csv

import pygame as pg

# ---------------------------------------------------------------- #

DELAY = 10

tile_names = ["circle", "cross", "diamond", "parallel", "plus", "square", "star", "triangle"]

icon = pg.image.load("images//icon.png")
bg_menu = pg.image.load("images//background.png")
bg_board = pg.image.load("images//board.png")

pg.mixer.init()
moving_player = [pg.mixer.Sound(f"sounds//moving_player_{i}.ogg") for i in [1, 2, 3, 4, 5, 6]]
moving_tiles = [pg.mixer.Sound(f"sounds//moving_tile_{i}.mp3") for i in [0, 1]]

adjacency_list = []
with open("adjacency_list.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    for from_key, from_rotation, move_key, to_key, to_rotation in csv_reader:
        adjacency_list.append((from_key, int(from_rotation), move_key, to_key, int(to_rotation)))

# ---------------------------------------------------------------- #
