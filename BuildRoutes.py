import networkx as nx
import itertools as it
import drawSvg as draw
import random

from Board import RESOURCES, BOARD, POSTS_TO_RESOURCES, get_dsts, distance

resource_to_all_routes = None
SHORT_ROUTE = [2, 5]
MED_ROUTE = [5, 8]
LONG_ROUTE = [8, 12]
FLAT_REWARD = 2


def make_triple_route(anchor, existing_routes=set(), board=BOARD):
    if anchor in RESOURCES:
        anchor_resource = anchor
        anchor_post = RESOURCES[anchor_resource]
    else:
        anchor_post = anchor
        anchor_resource = POSTS_TO_RESOURCES[anchor_post]

    short_routes = set(
        it.chain(
            *resource_to_all_routes[anchor_resource][SHORT_ROUTE[0] : SHORT_ROUTE[1]]
        )
    )
    short_routes = list(
        short_routes.difference(
            {dst for resource, dst in existing_routes if resource == anchor_resource}
        )
    )
    if len(short_routes) == 0:
        print(f"No short_routes left for {anchor_resource}")

    med_routes = set(
        it.chain(*resource_to_all_routes[anchor_resource][MED_ROUTE[0] : MED_ROUTE[1]])
    )
    med_routes = list(
        med_routes.difference(
            {dst for resource, dst in existing_routes if resource == anchor_resource}
        )
    )
    if len(med_routes) == 0:
        print(f"No med_routes left for {anchor_resource}")

    long_routes = set(
        it.chain(
            *resource_to_all_routes[anchor_resource][LONG_ROUTE[0] : LONG_ROUTE[1]]
        )
    )
    long_routes = list(
        long_routes.difference(
            {dst for resource, dst in existing_routes if resource == anchor_resource}
        )
    )
    if len(long_routes) == 0:
        print(f"No long_routes left for {anchor_resource}")

    return (
        (anchor_resource, short_routes[int(random.random() * len(short_routes))]),
        (anchor_resource, med_routes[int(random.random() * len(med_routes))]),
        (anchor_resource, long_routes[int(random.random() * len(long_routes))]),
    )


def flip_route(route):
    if route[1] in POSTS_TO_RESOURCES:
        return (POSTS_TO_RESOURCES[route[1]], RESOURCES[route[0]])


def make_all_triple_routes(board=BOARD):
    if resource_to_all_routes is None:
        resource_to_all_routes = {
            resource: [
                get_dsts(RESOURCES[resource], distance, BOARD)
                for distance in range(0, 12)
            ]
            for resource in RESOURCES
        }
    all_routes = []
    triple_list = []
    for resource in RESOURCES:
        while True:
            try:
                triple = make_triple_route(resource, all_routes)
            except IndexError:
                break

            triple_list.append(triple)
            all_routes.extend(triple)

    new_triple_list = []
    for triple in triple_list:
        new_triple = list(triple)
        random.shuffle(new_triple)
        for route in new_triple:
            flip = flip_route(route)
            if flip:
                triple = (flip, *[e for e in new_triple if e is not route])
                break

        new_triple_list.append(triple)

    return new_triple_list


def value_route(route):
    return (*route, distance(RESOURCES[route[0]], route[1]) + FLAT_REWARD)


def value_triple(triple):
    return tuple(
        sorted(
            (value_route(triple[0]), value_route(triple[1]), value_route(triple[2])),
            key=lambda x: -x[2],
        )
    )


def value_all_triples(triple_list):
    return [value_triple(triple) for triple in triple_list]