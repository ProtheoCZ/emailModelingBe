import random

import networkx as nx

from..utils import GraphTools as Gt

IGNORANT_TO_SPREADER = 0  # todo lambda
SPREADER_TO_STIFLER = 0  # todo alfa
CESSATION_RATE = 0  # todo delta
SPREADER = 'spreader'
STIFLER = 'stifler'
IGNORANT = 'ignorant'


def simulate_rumor_spread(graph_name):
    ret_json = {"graphs": [], "compatible": 0}
    json_graph = Gt.json_loader(graph_name)

    if isGraphCompatible(json_graph):
        graph = json_to_nx(json_graph)
        ret_graphs = rumor_spread(graph, True)
        for graph in ret_graphs:
            ret_json["graphs"].append(Gt.nx_to_json(graph))
        ret_json["compatible"] = 1


def isGraphCompatible(graph):
    try:
        random.sample(graph['nodes'], 1)[0]['population_group']
        return True
    except KeyError:
        return False


def json_to_nx(json_graph):
    graph = nx.Graph()

    for node in json_graph['nodes']:
        graph.add_node(
            node['id'],
            x=node['x'],
            y=node['y'],
            size=node['size'],
            displayed_color=node['color'],
            label=node['label'],
            id=node['id'],
            population_group=node['population_group'],
            rumor_group='ignorant'
        )

    for edge in json_graph['edges']:
        graph.add_edge(
            edge['source'],
            edge['target'],
            displayed_color=edge['color'],
            size=edge['size'],
            id=edge['id']
        )

    return graph


def rumor_spread(graph, is_hub_start: bool):
    if is_hub_start:
        start_node_id = Gt.get_hub_start(graph, Gt.HUB_THRESHOLD)
    else:
        start_node_id = random.sample(graph.nodes, 1)[0]

    ret_graph = nx.Graph()
    start_node = graph.nodes[start_node_id]
    start_node['rumor_group'] = SPREADER
    ret_graph.add_node(
        start_node_id,
        x=start_node['x'],
        y=start_node['y'],
        size=start_node['size'],
        displayed_color=start_node['displayed_color'],
        label=start_node['label'],
        id=start_node['id'],
        population_group=start_node['population_group'],
        rumor_group=start_node['rumor_group']
    )


    ret_graph = assign_visual_colors(ret_graph)
    ret_graphs = []

    return ret_graphs


def assign_visual_colors(graph):
    for node in graph.nodes:
        rumor_group = graph.nodes[node]['rumor_group']
        if rumor_group == SPREADER:
            graph.nodes[node]['displayed_color'] = Gt.SPREADER_COLOR
        elif rumor_group == STIFLER:
            graph.nodes[node]['displayed_color'] = Gt.STIFLER_COLOR
        elif rumor_group == IGNORANT:
            graph.nodes[node]['displayed_color'] = Gt.IGNORANT_COLOR

    return graph


def ignorant_to_spreader_chance(sender_node, receiver_node):
    # todo implement
    return 0


def spreader_to_stifler_chance(sender_node, receiver_node):
    # todo implement
    return 0


def cessation_chance(sender_node, receiver_node):
    # todo implement
    return 0



