# Copyright (c) 2022 Paul Vines

import networkx as nx
import itertools as it
import drawSvg as draw
import random


POST_CARD_SIZE = (200, 300)
COLOR_POST_STROKE = "#741b47"
COLOR_POST_FILL = "#ead1dcff"

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
    text_size = POST_CARD_SIZE[1] // 3
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
    canvas.savePng(f"cards/posts/{node}.png"
)

def draw_post_cards(board, posts_to_resources):
    for node in board.nodes():
        if "extra" not in node:
            draw_post(node, posts_to_resources)
