# ---------------------------------------------------------------- #

import os
import csv
import time
import pygame as pg

from constants import *
from classes import *

# ---------------------------------------------------------------- #

pg.init()

pg.display.set_caption("Temple-Trap")

pg.display.set_icon(icon)

# ---------------------------------------------------------------- #

def import_boards_album(screen):

    boards_album_members = []
    with open("boards.csv", "r") as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=";")
        next(csv_reader)

        for csv_name, csv_coordinates, csv_rotations, csv_player_coordinates in csv_reader:
            name = csv_name
            coordinates = {
                tile_name: (int(tile_coordinates_string[1]), int(tile_coordinates_string[3]))
                for tile_name, tile_coordinates_string in zip(
                    tile_names, csv_coordinates[1:-1].split(", ")
                )
            }
            rotations = {
                tile_name: int(tile_rotation_string)
                for tile_name, tile_rotation_string in zip(
                    tile_names, csv_rotations[1:-1].split(", ")
                )
            }
            player_coordinates = (int(csv_player_coordinates[1]), int(csv_player_coordinates[3]))
            boards_album_members.append(
                BoardEdit(screen, name, coordinates, rotations, player_coordinates)
            )

    return Album(screen, "boards album", members=boards_album_members)

def export_boards_album(boards_album):

    exportable_boards = [board for board in boards_album if board.full]
    if len(exportable_boards) > 0:
        with open("boards.csv", "w") as csv_file:

            csv_file.write("name;coordinates;rotations")

            for board in exportable_boards:

                name = board.name

                coordinates = {
                    member.name: board.field.mapping_position[i]
                    for i, member in enumerate(board.field.members)
                }
                coordinates = [
                    f"({coordinates[tile_name][0]}|{coordinates[tile_name][1]})"
                    for tile_name in tile_names
                ]
                coordinates = '[' + ', '.join(coordinates) + ']'

                rotations = str([
                    board.field[tile_name].rotation
                    for tile_name in tile_names
                ])

                player_coordinates = f"({board.player_coordinates[0]}|{board.player_coordinates[1]})"

                csv_file.write("\n" + f"{name};{coordinates};{rotations};{player_coordinates}")

# ---------------------------------------------------------------- #

def play(board):

    screen = pg.display.set_mode((720, 720))

    button_quit = Button(screen, f"button quit", x=720//2, y=720-64, width=128+64, height=64,
                         border_radius=32,
                         text_string="Quit", text_color=pg.Color("white"),
                         font_size=32, font_type="veranda bold",
                         filling_color_unclicked=pg.Color("yellow4"), filling_color_semiclicked=pg.Color("yellow3"), filling_color_clicked=pg.Color("yellow2"),
                         response="hold")

    game = Game(board)

    run = True
    while run:

        pg.time.delay(DELAY)

        screen.blit(bg_board, (0, 0))

        button_quit.draw()
        game.draw()

        pg.display.update()

        if game.finished:
            time.sleep(2)
            return True

        for event in pg.event.get():

            if event.type == pg.QUIT: return False

            button_quit.update(event)
            game.update(event)

            if button_quit.clicked(event) or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                if button_quit.clicked(event): random.choice(moving_tiles + moving_player).play()
                return True

def boards():

    screen = pg.display.set_mode((720, 720))

    boards_album = import_boards_album(screen)

    left = (3, 15); middle = (8, 15); right = (13, 15)
    buttons = Buttons(screen, "buttons",
                      grid_amount_rows=18, grid_amount_columns=18,
                      members=[
                        Button(screen, f"button {text_string.lower()}", width=128+64, height=64,
                               border_radius=32,
                               text_string=text_string, text_color=pg.Color("white"),
                               font_size=32, font_type="veranda bold",
                               filling_color_unclicked=pg.Color("yellow4"), filling_color_semiclicked=pg.Color("yellow3"), filling_color_clicked=pg.Color("yellow2"),
                               response="hold")
                        for text_string in ["Menu", "Back", "Next", "Play", "New Board"]
                      ],
                      mapping_position={"button menu": left, "button back": left, "button play": middle, "button next": right, "button new board": right},
                      mapping_nudge="inner")

    text_box_board_name = TextBox(screen, "text box board name", x=128, y=64, width=128+64, height=64,
                                  border_radius=32,
                                  text_color=pg.Color("black"),
                                  font_size=32, font_type="veranda bold",
                                  filling_color_unclicked=pg.Color("yellow4"), filling_color_semiclicked=pg.Color("yellow3"), filling_color_clicked=pg.Color("yellow2"),
                                  text_string_clicked=boards_album.page_current.name)

    run = True
    while run:

        pg.time.delay(DELAY)

        screen.blit(bg_board, (0, 0))
        boards_album.draw()

        if boards_album.on_first_page:
            buttons["button menu"].draw()
        else:
            buttons["button back"].draw()

        if boards_album.page_current.full:
            buttons["button play"].draw()

        if boards_album.on_last_page:
            buttons["button new board"].draw()
        else:
            if boards_album.pages_amount > 1:
                buttons["button next"].draw()

        text_box_board_name.draw()

        pg.display.update()

        for event in pg.event.get():

            if event.type == pg.QUIT: return False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                export_boards_album(boards_album)
                return True

            boards_album.update(event)

            if boards_album.on_first_page:
                buttons["button menu"].update(event)
                if buttons["button menu"].clicked(event):
                    random.choice(moving_tiles + moving_player).play()
                    export_boards_album(boards_album)
                    return True
            else:
                buttons["button back"].update(event)
                if buttons["button back"].clicked(event) or (event.type == pg.KEYDOWN and event.key == pg.K_LEFT):
                    if buttons["button back"].clicked(event): random.choice(moving_tiles + moving_player).play()
                    boards_album.move("back")
                    text_box_board_name.text_string_clicked = boards_album.page_current.name

            if boards_album.page_current.full:

                buttons["button play"].update(event)
                if buttons["button play"].clicked(event):

                    random.choice(moving_tiles + moving_player).play()

                    export_boards_album(boards_album)

                    tile_coordinates = {
                        member.name: boards_album.page_current.field.mapping_position[i]
                        for i, member in enumerate(boards_album.page_current.field.members)
                        if member.name != ""
                    }
                    tile_rotations = {
                        tile_name: boards_album.page_current.field[tile_name].rotation
                        for tile_name in tile_names
                    }
                    player_coordinates = boards_album.page_current.player_coordinates
                    board = Board(screen, tile_coordinates, tile_rotations, player_coordinates)

                    return play(board)

            if boards_album.on_last_page:
                buttons["button new board"].update(event)
                if buttons["button new board"].clicked(event):
                    random.choice(moving_tiles + moving_player).play()
                    boards_album.pages.append(BoardEdit(screen))
                    boards_album.move("next")
                    text_box_board_name.text_string_clicked = boards_album.page_current.name
            else:
                if boards_album.pages_amount > 1:
                    buttons["button next"].update(event)
                    if buttons["button next"].clicked(event) or (event.type == pg.KEYDOWN and event.key == pg.K_RIGHT):
                        if buttons["button next"].clicked(event): random.choice(moving_tiles + moving_player).play()
                        boards_album.move("next")
                        text_box_board_name.text_string_clicked = boards_album.page_current.name

            text_box_board_name.update(event)
            if text_box_board_name.clicked(event):
                random.choice(moving_tiles + moving_player).play()
            if text_box_board_name.clicked():
                boards_album.page_current.name = text_box_board_name.text_string_clicked

def menu():

    screen = pg.display.set_mode((512, 512))

    buttons = Buttons(screen, "buttons",
                      grid_amount_rows=10, grid_amount_columns=10,
                      members=[
                        Button(screen, f"button {text_string.lower()}", width=128+64, height=64,
                               border_radius=32,
                               text_string=text_string, text_color=pg.Color("white"),
                               font_size=32, font_type="veranda bold",
                               filling_color_unclicked=pg.Color("yellow4"), filling_color_semiclicked=pg.Color("yellow3"), filling_color_clicked=pg.Color("yellow2"),
                               response="hold")
                        for text_string in ["Boards", "Manual", "Quit"]
                      ],
                      mapping_position={"button boards": (3, 2), "button manual": (3, 4), "button quit": (3, 6)},
                      mapping_nudge="inner")

    run = True
    while run:

        pg.time.delay(DELAY)

        screen.blit(bg_menu, (0, 0))
        buttons.draw()

        pg.display.update()

        for event in pg.event.get():

            if event.type == pg.QUIT: return False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: return True

            buttons.update(event)

            if buttons["button quit"].clicked(event):
                sound = random.choice(moving_tiles + moving_player)
                sound.play()
                time.sleep(sound.get_length()-0.1)
                return False

            if buttons["button manual"].clicked(event):
                random.choice(moving_tiles + moving_player).play()
                os.startfile("manual.pdf")

            if buttons["button boards"].clicked(event):
                random.choice(moving_tiles + moving_player).play()
                run = boards()
                if run: screen = pg.display.set_mode((512, 512))

# ---------------------------------------------------------------- #

if __name__ == "__main__":
    menu()
    pg.quit()

# ---------------------------------------------------------------- #
