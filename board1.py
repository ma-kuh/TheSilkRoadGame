import  networkx as nx
import itertools as it
import drawSvg as draw
import random

edges = [
    ('Kiev','Cherson'),
    ('Cherson', 'extra1'),
    ('extra1', 'Atil'),
    ('Atil', 'extra2'),
    ('extra2', 'Bukhara'),
    ('Bukhara', 'extra3'),
    ('extra3', 'Samarkand'),
    ('Cherson', 'Constantinople'),
    ('Venice', 'Constantinople'),
    ('Constantinople', 'extra4'),
    ('extra4', 'Baku'),
    ('Constantinople', 'Alexandria'),
    ('Tripoli', 'Alexandria'),
    ('Alexandria', 'Palmyra'),
    ('Constantinople', 'Palmyra'),
    ('Palmyra', 'Baghdad'),
    ('Alexandria', 'Medina'),
    ('Medina', 'Baghdad'),
    ('Baghdad', 'Rayy'),
    ('Baku', 'Rayy'),
    ('Baku', 'Atil'),
    ('Rayy', 'Merv'),
    ('Merv', 'Samarkand'),
    ('Merv', 'Balkh'),
    ('Balkh', 'Delhi'),
    ('Delhi', 'extra5'),
    ('extra5', 'Khotan'),
    ('Samarkand', 'Kashgar'),
    ('Kashgar', 'Khotan'),
    ('Kashgar', 'Turfan'),
    ('Turfan', 'Dunhuang'),
    ('Khotan', 'Dunhuang'),
    ('Dunhuang', 'Xian'),
]

resources = {
    "silk": "Xian",
    "fur": "Kiev",
    "wine": "Venice",
    "glass": "Tripoli",
    "spices": "Delhi",
    "incense": "Medina"
}
posts_to_resources = {v:k for k,v in resources.items()}

FLAT_REWARD = 2

board = nx.Graph(edges)

def get_dsts(src, length, board=board):
    return {node  for node in board.nodes() if distance(src, node, board) == length and 'extra' not in node}

def distance(src,  dst,  board=board):
    return len(list(nx.shortest_simple_paths(board, src, dst))[0])

def res_distances(dst, resources={'venice', 'tripoli', 'xian', 'medina', 'kiev', 'delhi'}, board=board):
    return [(src, distance(src, dst, board)) for src in resources]

resource_to_all_routes = {
    resource:  [
        get_dsts(resources[resource], distance, board)
        for distance in  range(0, 12)
    ] for resource in resources
}
SHORT_ROUTE = [2, 5]
MED_ROUTE = [5, 8]
LONG_ROUTE = [8, 12]
def make_triple_route(anchor, existing_routes=set(), board=board):
    if anchor in  resources:
        anchor_resource = anchor
        anchor_post = resources[anchor_resource]
    else:
        anchor_post = anchor
        anchor_resource = posts_to_resources[anchor_post]
        
    short_routes = set(it.chain(*resource_to_all_routes[anchor_resource][SHORT_ROUTE[0]:SHORT_ROUTE[1]]))
    short_routes = list(short_routes.difference({
        dst for resource,dst in existing_routes
        if resource == anchor_resource
    }))
    if len(short_routes) == 0:
        print(f"No short_routes left for {anchor_resource}")

    med_routes = set(it.chain(*resource_to_all_routes[anchor_resource][MED_ROUTE[0]:MED_ROUTE[1]]))
    med_routes = list(med_routes.difference({
        dst for resource,dst in existing_routes
        if resource == anchor_resource
    }))
    if len(med_routes) == 0:
        print(f"No med_routes left for {anchor_resource}")


    long_routes = set(it.chain(*resource_to_all_routes[anchor_resource][LONG_ROUTE[0]:LONG_ROUTE[1]]))
    long_routes = list(long_routes.difference({
        dst for resource,dst in existing_routes
        if resource == anchor_resource
    }))
    if len(long_routes) == 0:
        print(f"No long_routes left for {anchor_resource}")

    return (
        (anchor_resource, short_routes[int(random.random() * len(short_routes))]),
        (anchor_resource, med_routes[int(random.random() * len(med_routes))]),
        (anchor_resource, long_routes[int(random.random() * len(long_routes))])
    )

def flip_route(route):
    if route[1] in posts_to_resources:
        return (posts_to_resources[route[1]],  resources[route[0]])


def make_all_triple_routes(board=board):
    all_routes = []
    triple_list = []
    for resource in resources:
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
    return (*route, distance(resources[route[0]], route[1]) + FLAT_REWARD)

def value_triple(triple):
    return tuple(sorted((
        value_route(triple[0]),
        value_route(triple[1]),
        value_route(triple[2]),
    ), key=lambda x: -x[2]
    ))

def value_all_triples(triple_list):
    return [value_triple(triple) for triple in triple_list]


def generate_contract_cards(num_cards=None):
    triple_list = make_all_triple_routes()
    valued = value_all_triples(triple_list)
    for idx, triple in enumerate(valued):
        draw_route_card(f"cards/contracts/{idx}", triple)
    

POST_CARD_SIZE = (200, 300)
COLOR_POST_STROKE = "#741b47"
COLOR_POST_FILL = "#ead1dcff"

ROUTE_CARD_SIZE = (600, 600)
CARD_BORDER = 6
COLOR_ROUTE_STROKE = "#b45f06"
COLOR_ROUTE_FILL = "#fce5cd"
ROUTE_X = ROUTE_CARD_SIZE[0] - CARD_BORDER
ROUTE_Y = (ROUTE_CARD_SIZE[1] -CARD_BORDER) // 3

class Space():
    def  __init__(self, x, y, width, height):
        self.x0 = x
        self.y0 = y
        self.x1 = x + width
        self.y1 = y + height
        self.width = width
        self.height = height


def draw_route(canvas, space, resource, dest, reward):
    canvas.append(draw.Rectangle(space.x0, space.y0, space.width, space.height,
                                 stroke_width=CARD_BORDER,
                                 stroke=COLOR_ROUTE_STROKE,
                                 fill=COLOR_ROUTE_FILL))
    spacing = CARD_BORDER
    text_size =  space.height // 3
    icon_diam = space.height // 2
    canvas.append(draw.Image(space.x0 + spacing,
                             space.y0 + space.height  // 4 + spacing,
                             icon_diam - spacing,
                             icon_diam - spacing,
                             path=f'images/{reward}coin.png',
                             embed=True))
    canvas.append(draw.Image(space.x0 + icon_diam + spacing,
                             space.y0 + space.height  // 4 + spacing,
                             icon_diam - spacing,
                             icon_diam - spacing,
                             path=f'images/{resource}.png',
                             embed=True))

    text_length= (space.width - (icon_diam * 2)) * (9 // 10)
    canvas.append(draw.Text(f"{dest}", text_size,
                            x=space.x0 + icon_diam * 2, 
                            y=space.y0 + (space.height // 3),
                            lengthAdjust="spacingAndGlyphs", 
                            textLength=text_length))
            

def draw_route_card(name, route_list):
    canvas = draw.Drawing(ROUTE_CARD_SIZE[0], ROUTE_CARD_SIZE[1])
    r = draw.Rectangle(0,0,ROUTE_CARD_SIZE[0],ROUTE_CARD_SIZE[1],
                       fill=COLOR_ROUTE_FILL,stroke_width=CARD_BORDER, stroke=COLOR_ROUTE_STROKE)
    canvas.append(r)

    for idx, route in enumerate(route_list):
        resource, dest, reward = route
        height = (ROUTE_CARD_SIZE[1] - CARD_BORDER*2) // 3
        space = Space(CARD_BORDER, (height * idx) + CARD_BORDER,
                      ROUTE_CARD_SIZE[0] - CARD_BORDER*2, height)
        draw_route(canvas, space, resource, dest, reward)
    
    print(canvas.allElements())
    canvas.saveSvg(f"{name}.svg")


def draw_post(node):
    canvas = draw.Drawing(POST_CARD_SIZE[0], POST_CARD_SIZE[1])
    canvas.append(draw.Rectangle(0,0,POST_CARD_SIZE[0],POST_CARD_SIZE[1],
                                 fill=COLOR_POST_FILL,stroke_width=CARD_BORDER, stroke=COLOR_POST_STROKE))
    text_size = POST_CARD_SIZE[1] // 3
    canvas.append(draw.Text(
        f"{node}", text_size,
        x=CARD_BORDER, y=POST_CARD_SIZE[1] * 2 // 3,
        lengthAdjust="spacingAndGlyphs",
        textLength=POST_CARD_SIZE[0] - (CARD_BORDER * 2)
    ))
    if node in posts_to_resources:
        diameter = POST_CARD_SIZE[0] // 3
        canvas.append(draw.Image((POST_CARD_SIZE[0] // 2) - (diameter // 2),
                                 (POST_CARD_SIZE[1] // 3) - (diameter // 2),
                                 diameter,
                                 diameter,
                                 path=f'images/{posts_to_resources[node]}.png',
                                 embed=True))
    canvas.saveSvg(f"cards/posts/{node}.svg")
    

def draw_post_cards():
    for node in board.nodes():
        if "extra" not in node:
            draw_post(node)

