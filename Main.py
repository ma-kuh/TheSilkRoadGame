# Copyright (c) 2022 Paul Vines

import networkx as nx
import itertools as it
import drawSvg as draw
import random

from BuildRoutes import make_all_triple_routes, value_all_triples
from Drawing import draw_route_card, draw_post_cards
from Board import BOARD, POSTS_TO_RESOURCES


def generate_contract_cards(num_cards=None):
    triple_list = make_all_triple_routes()
    valued = value_all_triples(triple_list)
    for idx, triple in enumerate(valued):
        draw_route_card(f"cards/contracts/{idx}", triple)


def generate_post_cards():
    draw_post_cards(BOARD, POSTS_TO_RESOURCES)
