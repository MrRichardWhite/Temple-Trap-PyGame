# ---------------------------------------------------------------- #

import random

import pygame as pg

from widgets.single import *
from widgets.multi import *

from constants import *

# ---------------------------------------------------------------- #

def reverse_dict(dictionary):
    return {value: key for key, value in dictionary.items()}

# ---------------------------------------------------------------- #

class Tile(Button):

    def __init__(self, surface, name, rotation=0):

        super().__init__(surface, name, width=138, height=138,
                         image_path=f"images//tiles//{name}.png", image_rotation=rotation*90,
                         response="hold")

        self.rotation = rotation

class Player(Label):

    def __init__(self, surface, name="player", coordinates=(0, 0), ghost=False):

        super().__init__(surface, name, width=138, height=138,
                         image_path=f"images//player.png" if not ghost else f"images//ghost_player.png")

        self.coordinates = coordinates

class Board(Buttons):

    def __init__(self, surface, tile_coordinates, tile_rotations, player_coordinates):

        super().__init__(surface, x=150, y=160, width=560-150, height=570-160,
                         grid_amount_rows=4, grid_amount_columns=4,
                         members=[Tile(surface, tile_name, tile_rotations[tile_name]) for tile_name in tile_names],
                         mapping_position=tile_coordinates,
                         mapping_nudge="inner")

        self.player = Player(surface, coordinates=player_coordinates)
        self.ghost_players = []

        self.update_tiles_position()
        self.update_player_position()

    def update_tiles_position(self):
        self.update_members_position()

    def update_player_position(self):
        self.player.position = self.grid_actually.inner[self.player.coordinates]

    def update_ghost_player_positions(self):
        for ghost_player in self.ghost_players:
            ghost_player.position = self.grid_actually.inner[ghost_player.coordinates]

    def tiles(self, key=None):

        if key is None:
            return zip(self.members,
                    (member.name for member in self.members),
                    (self.mapping_position[member.name] for member in self.members))

        elif type(key) is str:
            for tile, tile_name, tile_coordinates in self.tiles():
                if key == tile_name: return tile, tile_coordinates

        elif type(key) is tuple:
            for tile, tile_name, tile_coordinates in self.tiles():
                if key == tile_coordinates: return tile, tile_name

    @property
    def empty_tile(self):
        for x in range(3):
            for y in range(3):
                if (x, y) not in self.mapping_position.values():
                    return x, y

    def adjacent(self, key_1, key_2):

        if type(key_1) is str:
            for tile, tile_name, tile_coordinates in self.tiles():
                if tile_name == key_1:
                    tile_1 = tile
                    tile_name_1 = tile_name
                    x_1, y_1 = tile_coordinates
        if type(key_2) is str:
            for tile, tile_name, tile_coordinates in self.tiles():
                if tile_name == key_2:
                    tile_2 = tile
                    tile_name_2 = tile_name
                    x_2, y_2 = tile_coordinates

        if type(key_1) is tuple:
            for tile, tile_name, tile_coordinates in self.tiles():
                if tile_coordinates == key_1:
                    tile_1 = tile
                    tile_name_1 = tile_name
                    x_1, y_1 = tile_coordinates
        if type(key_2) is tuple:
            for tile, tile_name, tile_coordinates in self.tiles():
                if tile_coordinates == key_2:
                    tile_2 = tile
                    tile_name_2 = tile_name
                    x_2, y_2 = tile_coordinates

        if   x_1     == x_2 and y_1 - 1 == y_2: move_key = "up"
        elif x_1     == x_2 and y_1 + 1 == y_2: move_key = "down"
        elif x_1 - 1 == x_2 and y_1     == y_2: move_key = "left"
        elif x_1 + 1 == x_2 and y_1     == y_2: move_key = "right"
        else: return False

        return (tile_name_1, tile_1.rotation, move_key, tile_name_2, tile_2.rotation) in adjacency_list

    def neighbours(self, key, strictness=0):

        if strictness == -1:

            if type(key) is str:
                for _, name, coordinates in self.tiles():
                    if key == name:
                        x, y = coordinates

            if type(key) is tuple:
                x, y = key

            return (
                (x_new, y_new)
                for x_new, y_new in ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
                if 0 <= x_new < 3 and 0 <= y_new < 3
            )

        if strictness == 0:
            return (
                (*self.tiles(neighbour_coordinates), neighbour_coordinates)
                for neighbour_coordinates in self.neighbours(key, -1)
                if neighbour_coordinates != self.empty_tile
            )

        if strictness == 1:

            if type(key) is str:
                tile_name = key

            if type(key) is tuple:
                for _, name, coordinates in self.tiles():
                    if key == coordinates:
                        tile_name = name

            return (
                (neighbour, neighbour_name, neighbour_coordinates)
                for neighbour, neighbour_name, neighbour_coordinates in self.neighbours(key, 0)
                if self.adjacent(tile_name, neighbour_name)
            )

    def neighbour_names(self, key, strictness=0):
        assert strictness in [0, 1]
        return (neighbour_names for _, neighbour_names, _ in self.neighbours(key, strictness))

    def neighbour_coordinates(self, key, strictness=0):
        assert strictness in [0, 1, -1]
        if strictness == -1:
            return (neighbour_coordinates for neighbour_coordinates in self.neighbours(key, strictness))
        else:
            return (neighbour_coordinates for _, _, neighbour_coordinates in self.neighbours(key, strictness))

    def destinations_recursion(self, key):

        destinations_new = [
            (destination, destination_name, destination_coordinates)
            for destination, destination_name, destination_coordinates in self.neighbours(key, 1)
            if destination_name not in (_destination_name for _, _destination_name, _ in self._destinations)
        ]

        self._destinations += destinations_new

        for _, destination_new_name, _ in destinations_new:
            self.destinations_recursion(destination_new_name)

    def destinations(self, habitable=True):

        occupied_tile, occupied_tile_name, occupied_tile_coordinates = self.occupied_tile
        self._destinations = [(occupied_tile, occupied_tile_name, occupied_tile_coordinates)]
        self.destinations_recursion(occupied_tile_name)

        if habitable:
            return [
                (destination, destination_name, destination_coordinates)
                for destination, destination_name, destination_coordinates in self._destinations
                if not self.tile_occupied(destination_name) and destination_name not in ("parallel", "square", "plus")
            ]
        else:
            return self._destinations

    def destination_names(self):
        return (destination_name for _, destination_name, _ in self.destinations())

    def destination_coordinates(self):
        return (destination_coordinates for _, _, destination_coordinates in self.destinations())

    def tile_occupied(self, key):

        if type(key) is str:
            tile_name = key
            tile_coordinates = self.mapping_position[tile_name]

        if type(key) is tuple:
            tile_coordinates = key

        return tile_coordinates == self.player.coordinates

    def tile_semioccupied(self, key):

        if type(key) is str:
            tile_name = key
            tile_coordinates = self.mapping_position[tile_name]

        if type(key) is tuple:
            tile_coordinates = key

        return tile_coordinates in (ghost_player.coordinates for ghost_player in self.ghost_players)

    @property
    def occupied_tile(self):
        for tile, tile_name, tile_coordinates in self.tiles():
            if self.tile_occupied(tile_name):
                return tile, tile_name, tile_coordinates

    def draw(self):
        super().draw()
        self.player.draw()
        for ghost_player in self.ghost_players:
            ghost_player.draw()

    def update(self, event=None):
        for tile, tile_name, tile_coordinates in self.tiles():
            if tile.clicked(event):

                if not self.tile_occupied(tile_name):

                    if not self.tile_semioccupied(tile_name):
                        if self.empty_tile in self.neighbour_coordinates(tile_name, -1):
                            self.mapping_position[tile_name] = self.empty_tile
                            self.update_tiles_position()
                            random.choice(moving_tiles).play()
                    else:
                        self.player.coordinates = tile_coordinates
                        self.update_player_position()
                        random.choice(moving_player).play()

                    self.ghost_players = []

                else:
                    if len(self.ghost_players) == 0:
                        self.ghost_players = [
                            Player(self.surface, f"ghost player {i}", destination_coordinates, True)
                            for i, destination_coordinates in enumerate(self.destination_coordinates())
                        ]
                        self.update_ghost_player_positions()
                    else:
                        self.ghost_players = []

class Game(object):

    def __init__(self, board):
        self.board = board

    @property
    def surface(self):
        return self.board.surface

    def draw(self):
        self.board.draw()

    def update(self, event=None):
        self.board.update(event)

    @property
    def finished(self):

        finished = False
        for destination, destination_name, destination_coordinates in self.board.destinations(habitable=False):
            if destination_coordinates == (0, 0) and (destination_name, destination.rotation, "left", "exit", 1) in adjacency_list:
                finished = True

        return finished

# ---------------------------------------------------------------- #

class TileEditBench(Button):

    def __init__(self, surface, name, placed=False):

        if name == "player":
            super().__init__(surface, name, width=46+4, height=46+4,
                            scale_width=0.55, scale_height=0.55,
                            border_radius=46//2,
                            filling_color=pg.Color("black"),
                            image_scale_width=0.5, image_scale_height=0.5,
                            unclickable_outside=False)
        else:
            assert name in tile_names
            super().__init__(surface, name, width=138+4, height=138+4,
                            scale_width=0.55, scale_height=0.55,
                            border_radius=4,
                            filling_color=pg.Color("black"),
                            image_scale_width=0.5, image_scale_height=0.5,
                            unclickable_outside=False)

        self.placed = placed

    @property
    def placed(self):
        return self._placed

    @placed.setter
    def placed(self, placed):
        self._placed = placed
        self.image_path = "images//" + "tiles//" * (self.name != "player") + "ghost_" * self.placed + f"{self.name}.png"

class TileEditField(Button):

    def __init__(self, surface, name):

        self.initialized = False
        super().__init__(surface, name, width=138, height=138)
        self.initialized = True

    @property
    def rotation(self):
        return self.image_rotation // 90

    @rotation.setter
    def rotation(self, rotation):
        self.image_rotation = rotation * 90

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        if self.initialized:
            self.image_path = f"images//tiles//{name}.png" if name in tile_names else None

class BoardEditBench(Buttons):

    def __init__(self, surface, placed=False):

        super().__init__(surface,
                         grid_amount_rows=32+1, grid_amount_columns=32+1,
                         members=[TileEditBench(surface, name, placed=placed) for name in tile_names + ["player"]],
                         mapping_position={"circle": (2,  10), "cross":  (2,  14), "diamond": (2,  18), "parallel": (2,  22),
                                           "plus":   (29, 10), "square": (29, 14), "star":    (29, 18), "triangle": (29, 22),
                                           "player": (16, 3)},
                         mapping_nudge="inner")

        self.member_clicked_index = "player"

    def update(self, event):

        super().update(event)

        for i, member in enumerate(self.members):
            if i == self.member_clicked_index:
                member.filling_color = pg.Color("red")
            else:
                member.filling_color = pg.Color("black")

class BoardEditField(Buttons):

    def __init__(self, surface, coordinates=None, rotations=None):

        super().__init__(surface, x=150, y=160, width=560-150, height=570-160,
                         grid_amount_rows=4, grid_amount_columns=4,
                         members=[TileEditField(surface, "") for _ in range(9)],
                         mapping_position={n: (n % 3, n // 3) for n in range(9)},
                         mapping_nudge="inner")

        if coordinates is not None:
            for tile_name, tile_coordinates in coordinates.items():
                self[tile_coordinates].name = tile_name

        if rotations is not None:
            for tile_name, tile_rotation in rotations.items():
                self[tile_name].rotation = tile_rotation

class BoardEdit(Box):

    def __init__(self, surface, name="New Board", coordinates=None, rotations=None, player_coordinates=None):

        super().__init__(surface, name, anchor="north west")

        placed = coordinates is not None and rotations is not None and player_coordinates is not None
        if not placed:
            assert coordinates is None
            assert rotations is None
            assert player_coordinates is None

        self.bench = BoardEditBench(self.surface, placed=placed)
        self.field = BoardEditField(self.surface, coordinates, rotations)

        self.player = {"loaded": pg.image.load("images//player.png"), "coordinates": player_coordinates}

    @property
    def player_loaded(self):
        return self.player["loaded"]

    @property
    def player_coordinates(self):
        return self.player["coordinates"]

    @player_coordinates.setter
    def player_coordinates(self, player_coordinates):
        self.player["coordinates"] = player_coordinates

    @property
    def full(self):
        return False not in [tile.placed for tile in self.bench] and self.player_coordinates is not None

    def draw(self):
        self.bench.draw()
        self.field.draw()
        if self.player_coordinates is not None:
            x, y = self.field.grid_actually.inner[self.player_coordinates]
            x -= 46 // 2
            y -= 46 // 2
            self.surface.blit(self.player_loaded, (x, y))

    def occupied(self, tile_name):
        for i, tile in enumerate(self.field.members):
            if tile_name == tile.name:
                return self.player_coordinates == self.field.mapping_position[i]

    def update(self, event):

        for i, tile in enumerate(self.field):
            if tile.clicked(event):
                if tile.name == "":
                    if self.bench.member_clicked_index not in [None, 8]:
                        if not self.occupied(self.bench.member_clicked.name):

                            tile_name = self.bench.member_clicked.name
                            tile_rotation = 0

                            if tile_name in [other_tile.name for other_tile in self.field]:
                                tile_rotation = self.field[tile_name].rotation
                                self.field[tile_name].rotation = 0
                                self.field[tile_name].name = ""

                            tile.name = tile_name
                            self.bench.member_clicked.placed = True
                            random.choice(moving_tiles).play()
                            tile.rotation = tile_rotation

                else:

                    if self.player_coordinates == self.field.mapping_position[i]:
                        if self.bench.member_clicked_index != 8:
                            self.bench.member_clicked_index = "player"
                        else:
                            self.bench.member_clicked_index = None

                    if self.bench.member_clicked_index is not None:

                        if self.bench.member_clicked.name == tile.name:
                            random.choice(moving_tiles).play()
                            tile.rotation = (tile.rotation + 1) % 4

                        elif self.bench.member_clicked.name == "player" and tile.name not in ["parallel", "plus", "square"]:
                            if self.player_coordinates != self.field.mapping_position[i]:
                                random.choice(moving_player).play()
                            self.player_coordinates = self.field.mapping_position[i]
                            self.bench.member_clicked.placed = True

                        else:
                            self.bench.member_clicked_index = tile.name
                    else:
                        self.bench.member_clicked_index = tile.name

        self.bench.update(event)

        for tile in self.bench:
            if tile.clicked(event):
                if tile.placed:
                    if tile.name == "player":

                        self.player_coordinates = None
                        random.choice(moving_player).play()
                        self.bench["player"].placed = False

                    else:

                        if self.occupied(tile.name):
                            self.player_coordinates = None
                            random.choice(moving_player).play()
                            self.bench["player"].placed = False

                        self.field[tile.name].image_path = None
                        random.choice(moving_tiles).play()
                        tile.placed = False
                        self.field[tile.name].rotation = 0
                        self.field[tile.name].name = ""


# ---------------------------------------------------------------- #
