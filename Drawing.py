# Copyright (c) 2022 Paul Vines

import networkx as nx
import itertools as it
import drawSvg as draw
import os
import random
import subprocess


POST_CARD_SIZE = (200, 150)
COLOR_POST_STROKE = "#741b47"
COLOR_POST_FILL = "#ead1dc"

ROUTE_CARD_SIZE = (600, 600)
CARD_BORDER = 6
COLOR_ROUTE_STROKE = "#b45f06"
COLOR_ROUTE_FILL = "#fce5cd"
ROUTE_X = ROUTE_CARD_SIZE[0] - CARD_BORDER
ROUTE_Y = (ROUTE_CARD_SIZE[1] - CARD_BORDER) // 3


class Space:
    def __init__(self, x, y, width, height):
        self.x0 = x
        self.y0 = y
        self.x1 = x + width
        self.y1 = y + height
        self.width = width
        self.height = height


def draw_route(canvas, space, resource, dest, reward):
    canvas.append(
        draw.Rectangle(
            space.x0,
            space.y0,
            space.width,
            space.height,
            stroke_width=CARD_BORDER,
            stroke=COLOR_ROUTE_STROKE,
            fill=COLOR_ROUTE_FILL,
        )
    )
    spacing = CARD_BORDER
    text_size = space.height // 3
    icon_diam = space.height // 2
    canvas.append(
        draw.Image(
            space.x0 + spacing,
            space.y0 + space.height // 4 + spacing,
            icon_diam - spacing,
            icon_diam - spacing,
            path=f"images/{reward}coin.png",
            embed=True,
        )
    )
    canvas.append(
        draw.Image(
            space.x0 + icon_diam + spacing,
            space.y0 + space.height // 4 + spacing,
            icon_diam - spacing,
            icon_diam - spacing,
            path=f"images/{resource}.png",
            embed=True,
        )
    )

    text_length = (space.width - (icon_diam * 2)) * (9 // 10)
    canvas.append(
        draw.Text(
            f"{dest}",
            text_size,
            x=space.x0 + icon_diam * 2,
            y=space.y0 + (space.height // 3),
            lengthAdjust="spacingAndGlyphs",
            textLength=text_length,
        )
    )


def draw_route_card(name, route_list):
    canvas = draw.Drawing(ROUTE_CARD_SIZE[0], ROUTE_CARD_SIZE[1])
    r = draw.Rectangle(
        0,
        0,
        ROUTE_CARD_SIZE[0],
        ROUTE_CARD_SIZE[1],
        fill=COLOR_ROUTE_FILL,
        stroke_width=CARD_BORDER,
        stroke=COLOR_ROUTE_STROKE,
    )
    canvas.append(r)

    for idx, route in enumerate(route_list):
        resource, dest, reward = route
        height = (ROUTE_CARD_SIZE[1] - CARD_BORDER * 2) // 3
        space = Space(
            CARD_BORDER,
            (height * idx) + CARD_BORDER,
            ROUTE_CARD_SIZE[0] - CARD_BORDER * 2,
            height,
        )
        draw_route(canvas, space, resource, dest, reward)

    canvas.savePng(f"{name}.png")


def draw_post(node, posts_to_resources):
    canvas = draw.Drawing(POST_CARD_SIZE[0], POST_CARD_SIZE[1])
    canvas.append(
        draw.Rectangle(
            0,
            0,
            POST_CARD_SIZE[0],
            POST_CARD_SIZE[1],
            fill=COLOR_POST_FILL,
            stroke_width=CARD_BORDER,
            stroke=COLOR_POST_STROKE,
        )
    )
    text_size = POST_CARD_SIZE[1] // 4
    canvas.append(
        draw.Text(
            f"{node}",
            text_size,
            x=CARD_BORDER,
            y=POST_CARD_SIZE[1] * 2 // 3,
            lengthAdjust="spacingAndGlyphs",
            textLength=POST_CARD_SIZE[0] - (CARD_BORDER * 2),
        )
    )
    if node in posts_to_resources:
        diameter = POST_CARD_SIZE[0] // 3
        canvas.append(
            draw.Image(
                (POST_CARD_SIZE[0] // 2) - (diameter // 2),
                (POST_CARD_SIZE[1] // 3) - (diameter // 2),
                diameter,
                diameter,
                path=f"images/{posts_to_resources[node]}.png",
                embed=True,
            )
        )
    canvas_to_png(canvas, node)


def canvas_to_png(canvas, name):
    canvas.saveSvg(f"tmp/{name}.svg")
    subprocess.call(
        [
            "inkscape",
            "-z",
            "-e",
            f"cards/posts/{name}.png",
            f"tmp/{name}.svg",
        ]
    )


def draw_post_cards(board, posts_to_resources):
    for node in board.nodes():
        if "extra" not in node:
            draw_post(node, posts_to_resources)


GAME_SIZE = [9_000, 9_000]
BOARD_IMG_SIZE = (5704, 2425)
HOR_PLAYMAT_SIZE = (1_000, 5_000)
VER_PLAYMAT_SIZE = (HOR_PLAYMAT_SIZE[1], HOR_PLAYMAT_SIZE[0])
BANK_SIZE = (5_000, 1_000)


def setup_game(num_players=3):
    canvas = draw.Drawing(GAME_SIZE[0], GAME_SIZE[1])

    top_space = (
        GAME_SIZE[1] - (VER_PLAYMAT_SIZE[1] * (num_players % 3)) - BOARD_IMG_SIZE[1]
    )
    board_space = Space(
        (
            HOR_PLAYMAT_SIZE[0]
            + (GAME_SIZE[0] - HOR_PLAYMAT_SIZE[0] * 2 - BOARD_IMG_SIZE[0]) // 2
        ),
        top_space,
        BOARD_IMG_SIZE[0],
        BOARD_IMG_SIZE[1],
    )
    canvas.append(
        draw.Image(
            board_space.x0,
            board_space.y0,
            board_space.width,
            board_space.height,
            path=f"images/board.png",
            embed=True,
        )
    )

    left_mat_space = Space(
        0, GAME_SIZE[1] - HOR_PLAYMAT_SIZE[1], HOR_PLAYMAT_SIZE[0], HOR_PLAYMAT_SIZE[1]
    )
    draw_playmat(canvas, left_mat_space, "blue")

    right_mat_space = Space(
        GAME_SIZE[0] - HOR_PLAYMAT_SIZE[0],
        GAME_SIZE[1] - HOR_PLAYMAT_SIZE[1],
        HOR_PLAYMAT_SIZE[0],
        HOR_PLAYMAT_SIZE[1],
    )
    draw_playmat(canvas, right_mat_space, "red")

    bottom_mat_space = Space(
        (GAME_SIZE[0] - VER_PLAYMAT_SIZE[0]) // 2,
        top_space - BOARD_IMG_SIZE[1],
        VER_PLAYMAT_SIZE[0],
        VER_PLAYMAT_SIZE[1],
    )
    draw_playmat(canvas, bottom_mat_space, "green")

    if num_players > 3:
        top_mat_space = Space(
            (GAME_SIZE[0] - VER_PLAYMAT_SIZE[0]) // 2,
            top_space + BOARD_IMG_SIZE[1],
            VER_PLAYMAT_SIZE[0],
            VER_PLAYMAT_SIZE[1],
        )
        draw_playmat(canvas, top_mat_space, "yellow")

    bank_space = Space(
        bottom_mat_space.x0, top_space - BANK_SIZE[1], BANK_SIZE[0], BANK_SIZE[1]
    )
    draw_bank(canvas, bank_space)

    contract_deck_space = Space(
        GAME_SIZE[0] // 2,
        bottom_mat_space.y0 - (GAME_SIZE[1] // 10),
        POST_CARD_SIZE[0],
        POST_CARD_SIZE[1],
    )
    draw_contract_deck(canvas, contract_deck_space)

    # canvas.savePng(f"board.png")
    canvas.saveSvg(f"board.svg")


def draw_contract_deck(canvas, space):
    contract_files = [fn for fn in os.listdir("cards/contracts") if ".png" in fn]
    print(contract_files)
    for file in contract_files:
        canvas.append(
            draw.Image(
                space.x0,
                space.y0,
                space.width,
                space.height,
                path=f"cards/contracts/{file}",
                embed=True,
            )
        )


BANK_COLOR = "white"
COIN_SIZE = (150, 150)
MARKER_SIZE = (100, 100)


def draw_bank(canvas, space):
    canvas.append(
        draw.Rectangle(
            space.x0,
            space.y0,
            space.width,
            space.height,
            stroke_width=CARD_BORDER,
            stroke=BANK_COLOR,
            fill=BANK_COLOR,
        )
    )
    for value in (1, 3, 5, 10):
        for idx in range(10):
            canvas.append(
                draw.Image(
                    space.x0 + (random.random() * BANK_SIZE[0] // 3),
                    space.y0 + (5 * random.random() * BANK_SIZE[1] // 6),
                    COIN_SIZE[0],
                    COIN_SIZE[1],
                    path=f"images/{value}coin.png",
                    embed=True,
                )
            )

    for value in (1, 3, 5, 10):
        for idx in range(10):
            canvas.append(
                draw.Image(
                    space.x0
                    + ((random.random() * BANK_SIZE[0] // 3) + (BANK_SIZE[0] // 2)),
                    space.y0 + (5 * random.random() * BANK_SIZE[1] // 6),
                    COIN_SIZE[0],
                    COIN_SIZE[1],
                    path=f"images/{value}point.png",
                    embed=True,
                )
            )


STARTING_COINS = (1, 1, 1, 1, 3, 3)


def draw_playmat(canvas, space, color):
    canvas.append(
        draw.Rectangle(
            space.x0,
            space.y0,
            space.width,
            space.height,
            stroke_width=CARD_BORDER,
            stroke=color,
            fill=color,
        )
    )

    # Draw starting coins
    for idx, value in enumerate(STARTING_COINS):
        canvas.append(
            draw.Image(
                space.x0 + idx * COIN_SIZE[0],
                space.y0 + ((space.height * 5) // 10),
                COIN_SIZE[0],
                COIN_SIZE[1],
                path=f"images/{value}coin.png",
                embed=True,
            )
        )

    # TODO replace with faction-colored ownership markers
    for idx in range(25):
        canvas.append(
            draw.Rectangle(
                space.x0,
                space.y0 + ((space.height * 5) // 10) - MARKER_SIZE[1],
                MARKER_SIZE[0],
                MARKER_SIZE[1],
                fill=color,
                stroke="white",
                stroke_width=MARKER_SIZE[0] // 10,
                embed=True,
            )
        )

    # TODO replace with faction-colored route markers
    for idx in range(25):
        canvas.append(
            draw.Rectangle(
                space.x0,
                space.y0 + ((space.height * 5) // 10) - MARKER_SIZE[1] * 2,
                MARKER_SIZE[0],
                MARKER_SIZE[1],
                fill=color,
                stroke="white",
                stroke_width=MARKER_SIZE[0] // 10,
                embed=True,
            )
        )
    # TOOO faction markers,  route markers
