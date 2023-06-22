import json
import random
import os
from ..utils import GraphTools as Gt
from ..utils import StatsProvider as Sp

import networkx as nx

BASE_PROBABILITY = 0.75  # probability denotes chance NOT to respond
POST_COLOR = 'rgb(0,255,0)'
RESPONSE_COLOR = 'rgb(0,0,255)'
START_COLOR = 'rgb(242,245,66)'
LNK_POST_RATE = 0.22

start_node_id = 'xxx'


def simulate_relatability(graph_name):
    ret_json = {"graphs": [], "compatible": 0}
    json_graph = Gt.json_loader(graph_name)

    if isGraphCompatibleLite(json_graph):
        graph = json_to_nx(json_graph)
        ret_graphs = age_relatability(graph, True, True)
        for graph in ret_graphs:
            ret_json["graphs"].append(Gt.nx_to_json(graph))
        ret_json["compatible"] = 1

    return ret_json


def run_full_relatability(graph_name, run_count, is_hub_start: bool, export_stats=True):
    json_graph = Gt.json_loader(graph_name)
    if isGraphCompatibleLite(json_graph):
        sim_id = Sp.get_sim_id()
        if export_stats:
            os.mkdir(Sp.FULL_SIM_DIR + '/Sim_' + str(sim_id))
        graph = json_to_nx(json_graph)
        for i in range(run_count):
            graphs = age_relatability(graph, is_hub_start, True)  # todo graph.copy()???

            if export_stats:
                result_graph = graphs[0]
                tree = graphs[1]
                Sp.get_stats(tree,
                             start_node_id,
                             graph_name,
                             is_hub_start,
                             i+1,
                             sim_id,
                             result_graph
                             )

            print("run #" + str(i + 1) + " of " + str(run_count))

        if export_stats:
            Sp.get_summary_stats(sim_id, "age relatability")


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
            age=node['attributes']['age'],
            gender=node['attributes']['gender']
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


def age_relatability(graph, is_hub_start: bool, with_lnk_coloring=False):
    ret_graph = nx.Graph()
    global start_node_id
    if is_hub_start:
        start_node_id = Gt.get_hub_start(graph, Gt.HUB_THRESHOLD)
    else:
        start_node_id = random.sample(graph.nodes, 1)[0]

    start_node = graph.nodes[start_node_id]
    ret_graph.add_node(
        start_node_id,
        x=start_node['x'],
        y=start_node['y'],
        size=start_node['size'],
        displayed_color=START_COLOR,
        label=start_node['label'],
        id=start_node_id,
        age=start_node['age'],
        gender=start_node['gender']
    )
    active_nodes = [start_node_id]
    visited_nodes = [start_node_id]

    current_node_idx = 0
    current_node = start_node_id
    edge_id = 0
    while len(active_nodes) > current_node_idx:
        current_age = graph.nodes[current_node]['age']
        neighbors = nx.neighbors(graph, current_node)
        for node_id in neighbors:
            if node_id not in visited_nodes:
                visited_nodes.append(node_id)
                age = graph.nodes[node_id]['age']
                total_probability = calculate_probability(current_age, age)

                if random.random() > total_probability:  # todo < or > ?
                    active_nodes.append(node_id)
                    node = graph.nodes[node_id]
                    color = node['displayed_color']
                    if with_lnk_coloring:
                        if random.random() < LNK_POST_RATE:
                            color = POST_COLOR
                        else:
                            color = RESPONSE_COLOR

                    ret_graph.add_node(
                        node_id,
                        x=node['x'],
                        y=node['y'],
                        size=node['size'],
                        displayed_color=color,
                        label=node['label'],
                        id=node_id,
                        age=node['age'],
                        gender=node['gender']
                    )
                    ret_graph.add_edge(
                        current_node,
                        node_id,
                        displayed_color='rgb(0,0,0)',
                        size=1,
                        id=edge_id
                    )
                    edge_id += 1
        current_node_idx += 1
        if len(active_nodes) > current_node_idx + 1:
            current_node = active_nodes[current_node_idx]

    ret_array = [ret_graph]
    if with_lnk_coloring:
        ret_tree = Gt.treeify(ret_graph)
        ret_array.append(ret_tree)

        if nx.is_tree(ret_tree):
            ordered_tree = Gt.order_tree(ret_tree, start_node_id)
            ret_array.append(ordered_tree)

    return ret_array


def calculate_probability(current_age, age):
    age_diff = abs(int(current_age) - int(age))
    age_probability = age_diff / 100
    total_probability = age_probability + BASE_PROBABILITY
    if total_probability > 0.99:
        total_probability = 0.99
    return total_probability


# checks random node attrs needed by alg, maybe implement function checking all nodes
def isGraphCompatibleLite(graph):
    try:
        random.sample(graph['nodes'], 1)[0]['attributes']['gender']
        random.sample(graph['nodes'], 1)[0]['attributes']['age']
        return True
    except KeyError:
        return False
