# Copyright (c) 2022 Paul Vines

import networkx as nx
import itertools as it
import drawSvg as draw
import random
import sys

from BuildRoutes import gen_contracts_for_resources, value_all_triples
from Drawing import stdout_contract_card, draw_contract_card, draw_post_cards
from Board import BOARD, POSTS_TO_RESOURCES

def generate_contract_cards(num_cards=None):
    valued = gen_contracts_for_resources()
    for idx, triple in enumerate(valued):
        draw_contract_card(f"cards/contracts/{idx}", triple)

def stdout_contract_cards(num_cards=None):
    valued = gen_contracts_for_resources()
    for idx, triple in enumerate(valued):
        if 'csv' in sys.argv:
            stdout_contract_card(triple, '', ',')
        else:
            stdout_contract_card(triple, f"- Route {idx}")

def generate_post_cards():
    draw_post_cards(BOARD, POSTS_TO_RESOURCES)


if __name__ == "__main__":
    stdout_contract_cards()
