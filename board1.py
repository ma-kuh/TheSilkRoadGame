import  networkx as nx
import itertools as it
import drawSvg as draw

edges = [
    ('kiev','cherson'),
    ('cherson', 'extra1'),
    ('extra1', 'atil'),
    ('atil', 'extra2'),
    ('extra2', 'bukhara'),
    ('bukhara', 'extra3'),
    ('extra3', 'samarkand'),
    ('cherson', 'constantinople'),
    ('venice', 'constantinople'),
    ('constantinople', 'extra4'),
    ('extra4', 'baku'),
    ('constantinople', 'alexandria'),
    ('tripoli', 'alexandria'),
    ('alexandria', 'palmyra'),
    ('constantinople', 'palmyra'),
    ('palmyra', 'baghdad'),
    ('alexandria', 'medina'),
    ('medina', 'baghdad'),
    ('baghdad', 'rayy'),
    ('baku', 'rayy'),
    ('baku', 'atil'),
    ('rayy', 'merv'),
    ('merv', 'samarkand'),
    ('merv', 'balkh'),
    ('balkh', 'delhi'),
    ('delhi', 'extra5'),
    ('extra5', 'khotan'),
    ('samarkand', 'kashgar'),
    ('kashgar', 'khotan'),
    ('kashgar', 'turfan'),
    ('turfan', 'dunhuang'),
    ('khotan', 'dunhuang'),
    ('dunhuang', 'xian'),
]

board = nx.Graph(edges)

def get_dsts(src, length, board=board):
    return {node  for node in board.nodes() if distance(src, node, board) == length}

def distance(src,  dst,  board=board):
    return len(list(nx.shortest_simple_paths(board, src, dst))[0])

def res_distances(dst, resources={'venice', 'tripoli', 'xian', 'medina', 'kiev', 'delhi'}, board=board):
    return [(src, distance(src, dst, board)) for src in resources]


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

def embed_image(canvas, filename, x=0, y=0, w=0, h=0, center=None):
    if center is not None:
        if x != 0 and y != 0:
            print("Error: either pass x and y (upper left corner) OR a center coordinate")
            
        x = center[0] - w//2
        y = center[1] - h//2

    canvas.append(draw.Image(x, y, w, h,
                             path=filename,
                             embed=True))
    

import magic
def img_to_datauri(filepath):
    mime_str = magic.Magic(mime=True).from_file(filepath)
    data = base64.b64encode(open(filepath, 'rb').read()) 
    data_uri = f'data:{mime_str};base64,{data}'
    return data_uri
 
    
