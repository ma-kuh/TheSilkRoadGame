# Copyright (c) 2022 Paul Vines

import networkx as nx
import itertools as it
import drawSvg as draw
import random

from Board import IMPORTANT_DESTS, GATEWAYS, GW_TO_SOURCE, DM, REAL_NODES, RESOURCES, BOARD, POSTS_TO_RESOURCES, get_dsts, distance

resource_to_all_routes = None
SHORT_ROUTE = [2, 4]
MED_ROUTE = [4, 7]
LONG_ROUTE = [7, 12]
FLAT_REWARD = 2

dst_contracts = set()

def gen_outposts():
    resource_to_outposts = {}
    for gw in GATEWAYS.values():
        neighbors = set(nx.neighbors(board, gw))
        sources = {n for n in neighbors if n in POSTS_TO_RESOURCES}
        for s in sources:
            resource_to_outposts[s] = {n for n in neighbors if n not in sources}
        
    return resource_to_outposts

def gen_nml():
    non_nml = set(GATEWAYS.keys()).union(set(GATEWAYS.values()))
    return {n for n in REAL_NODES if n not in non_nml}

        
def gen_all_routes():
    min_dist = 2
    resource_to_outposts = gen_outposts(board)

    short_routes = [(res, dst, DM[src][dst]) for res,src in RESOURCES.items() for dst in REAL_NODES if DM[src][dst] in range(*SHORT_ROUTE)]
    med_routes = [(res, dst, DM[src][dst]) for res,src in RESOURCES.items() for dst in REAL_NODES if DM[src][dst] in range(*MED_ROUTE)]
    long_routes = [(res, dst, DM[src][dst]) for res,src in RESOURCES.items() for dst in REAL_NODES if DM[src][dst] in range(*LONG_ROUTE)]

    return short_routes,med_routes,long_routes


def gen_pref_gw_routes(src, dist_range):
    routes = [(src, dst) for dst in GATEWAYS.values() if DM[src][dst] in dist_range]
    if len(routes) == 0:
        routes = [(src, dst) for dst in gen_nml() if DM[src][dst] in dist_range]

    random.shuffle(routes)
    return routes


def gen_routes_for_dst(dst, dist_range):
    routes = [(src, dst) for src in RESOURCES.values() if DM[src][dst] in dist_range]
    random.shuffle(routes)
    return routes


def gen_nml_routes(src, dist_range):
    routes = [(src, dst) for dst in gen_nml() if DM[src][dst] in dist_range]
    random.shuffle(routes)
    return routes


def gen_start_contract(resource):
    src = RESOURCES[resource]
    shorts = gen_pref_gw_routes(src, range(*SHORT_ROUTE))
    meds = gen_pref_gw_routes(src, range(*MED_ROUTE))
    longs = gen_routes_for_dst(GATEWAYS[src], range(*LONG_ROUTE))
    return (shorts[0], meds[0], longs[0])


def gen_typical_contract(resource):
    src = RESOURCES[resource]
    shorts = gen_pref_gw_routes(src, range(*SHORT_ROUTE))
    meds = gen_nml_routes(src, range(*MED_ROUTE))
    longs = gen_routes_for_dst(GATEWAYS[src], range(*LONG_ROUTE))
    return (shorts[0], meds[0], longs[0])


def gen_narrow_contract(resource):
    src = RESOURCES[resource]
    to_gw = gen_pref_gw_routes(src, range(SHORT_ROUTE[0], MED_ROUTE[1]))[0]
    other_src = GW_TO_SOURCE[to_gw[1]]
    from_source = (other_src, src)
    to_source = (src, other_src)
    return (to_gw, from_source, to_source)


def gen_3res_contract(resource):
    src = RESOURCES[resource]
    gw = GATEWAYS[src]
    r1 = gen_routes_for_dst(gw, range(SHORT_ROUTE[0], MED_ROUTE[1]))[0]
    r2 = gen_routes_for_dst(gw, range(MED_ROUTE[0], LONG_ROUTE[1]))[0]
    while (r1[0] == r2[0]):
        r2 = gen_routes_for_dst(gw, range(MED_ROUTE[0], LONG_ROUTE[1]))[0]
        
    from_src = gen_nml_routes(src, range(MED_ROUTE[0], LONG_ROUTE[1]))[0]
    return (r1, r2, from_src)


def gen_dst_contract(resource=None):
    global dst_contracts
    nml = list(IMPORTANT_DESTS.difference(dst_contracts))
    random.shuffle(nml)
    dst = nml[0]
    dst_contracts.add(dst)
    
    return gen_routes_for_dst(dst, range(SHORT_ROUTE[0], LONG_ROUTE[1]))[:3]
 

def gen_src_contract(resource):
    src = RESOURCES[resource]
    routes = []
    for dist_range in [range(*SHORT_ROUTE), range(*MED_ROUTE), range(*LONG_ROUTE)]:
        route = gen_pref_gw_routes(src, dist_range)[0]
        routes.append((src, GW_TO_SOURCE.get(route[1], route[1])))

    return routes


contract_dist_per_resource = {
    gen_typical_contract: 3,
    gen_narrow_contract: 1,
    gen_3res_contract: 1,
    gen_dst_contract: 1,
    gen_src_contract: 1,
}


def value_route(route):
    resource = POSTS_TO_RESOURCES[route[0]]
    return (resource, route[1], distance(route[0], route[1]) + FLAT_REWARD)


def value_triple(triple):
    return tuple(
        sorted(
            (value_route(triple[0]), value_route(triple[1]), value_route(triple[2])),
            key=lambda x: -x[2],
        )
    )


def value_all_triples(triple_list):
    return [value_triple(triple) for triple in triple_list]


def gen_contracts_for_resources():
    contract_stems = []
    for res in RESOURCES.keys():
        for func, count in contract_dist_per_resource.items():
            for _ in range(count):
                contract = func(res)
                # print(str(func), contract)
                if contract is None:
                    print(f"ERROR: {str(func)} {res}")
                    continue
                    
                if any(len(r) == 0 for r in contract):
                    print(f"ERROR: {str(func)} {res} {contract}")
                    continue
                
                contract_stems.append(contract)

    for res in RESOURCES.keys():
        contract_stems.append(gen_start_contract(res))

    valued = value_all_triples(contract_stems)
    return valued
