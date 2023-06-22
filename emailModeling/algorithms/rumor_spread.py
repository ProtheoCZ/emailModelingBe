import random

import networkx as nx

from ..utils import GraphTools as Gt

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

    return ret_json


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
            rumor_group=IGNORANT
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

    queue = []  # (sender, receiver)
    current_edge_id = 1

    for neighbor in graph.neighbors(start_node_id):
        convert_ignorant(start_node_id, neighbor, graph, queue, ret_graph, current_edge_id)
        current_edge_id += 1

    while len(queue) > 0:
        current_node_pair = queue.pop(0)
        current_node_id = current_node_pair[1]

        for neighbor in graph.neighbors(current_node_id):
            neighbor_rumor_group = graph.nodes[neighbor]['rumor_group']

            if random.random() < cessation_chance(current_node_id, neighbor):
                if neighbor_rumor_group == IGNORANT:
                    convert_ignorant(current_node_id, neighbor, graph, queue, ret_graph, current_edge_id)
                    current_edge_id += 1
                elif neighbor_rumor_group == SPREADER or neighbor_rumor_group == STIFLER:
                    alfa_chance = spreader_to_stifler_chance(current_node_id, neighbor)
                    if random.random() < alfa_chance:
                        graph.nodes[current_node_id]['rumor_group'] = STIFLER
                        ret_graph.nodes[current_node_id]['rumor_group'] = STIFLER

    assign_visual_colors(ret_graph)
    ret_graphs = [ret_graph]

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


# Whenever a spreader contacts an ignorant, the ignorant becomes a spreader at a rate lambda.
def ignorant_to_spreader_chance(sender_node, receiver_node):
    # todo implement
    return 0.7


# When a spreader contacts another spreader or a stifler the initiating spreader becomes a stifler at a rate alfa.
def spreader_to_stifler_chance(sender_node, receiver_node):
    # todo implement
    return 0.6


def cessation_chance(sender_node, receiver_node):
    # todo implement
    return 0.5


def convert_ignorant(current_node_id, neighbor, graph, queue, ret_graph,current_edge_id):
    lambda_chance = ignorant_to_spreader_chance(current_node_id, neighbor)
    if random.random() < lambda_chance:
        graph.nodes[neighbor]['rumor_group'] = SPREADER
        queue.append((current_node_id, neighbor))
        ret_graph.add_node(
            neighbor,
            x=graph.nodes[neighbor]['x'],
            y=graph.nodes[neighbor]['y'],
            size=graph.nodes[neighbor]['size'],
            displayed_color=graph.nodes[neighbor]['displayed_color'],
            label=graph.nodes[neighbor]['label'],
            id=graph.nodes[neighbor]['id'],
            population_group=graph.nodes[neighbor]['population_group'],
            rumor_group=graph.nodes[neighbor]['rumor_group']
        )

        ret_graph.add_edge(
            current_node_id,
            neighbor,
            displayed_color=Gt.RESPONSE_EDGE_COLOR,
            size=1,
            id=current_edge_id
        )
