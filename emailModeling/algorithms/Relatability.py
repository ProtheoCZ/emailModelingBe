import json
import random

import networkx as nx

BASE_PROBABILITY = 0.65  # probability denotes chance NOT to respond


def simulate_relatability(graph_name):
    ret_json = {"graphs": [], "compatible": 0}
    json_graph = json_loader(graph_name)

    if isGraphCompatibleLite(json_graph):
        graph = json_to_nx(json_graph)
        ret_graph = age_relatability(graph)
        ret_json["graphs"].append(nx_to_json(ret_graph))
        ret_json["compatible"] = 1

    return ret_json


def json_loader(json_graph_name):
    file = open('GraphData/' + json_graph_name)
    json_file = json.load(file)
    return json_file


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


def nx_to_json(graph):
    ret_json = {
        "nodes": [],
        "edges": []
    }
    for node in graph.nodes:
        json_node = {
            "label": graph.nodes[node]["label"],
            "x": graph.nodes[node]["x"],
            "y": graph.nodes[node]["y"],
            "id": graph.nodes[node]["id"],
            "attributes": {},
            "color": graph.nodes[node]["displayed_color"],
            "size": graph.nodes[node]["size"]
        }
        ret_json["nodes"].append(json_node)

    for edge in graph.edges:
        json_edge = {
            "source": edge[0],
            "target": edge[1],
            "id": graph.edges[edge]["id"],
            "attributes": {},
            "color": graph.edges[edge]["displayed_color"],
            "size": graph.edges[edge]["size"],
        }
        ret_json["edges"].append(json_edge)

    return ret_json


def age_relatability(graph):
    ret_graph = nx.Graph()
    # start_node = graph.nodes[str(random.randint(1, graph.number_of_nodes()))]
    start_node_id = random.sample(graph.nodes, 1)[0]
    start_node = graph.nodes[start_node_id]
    ret_graph.add_node(
        start_node_id,
        x=start_node['x'],
        y=start_node['y'],
        size=start_node['size'],
        displayed_color=start_node['displayed_color'],
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
                    ret_graph.add_node(
                        node_id,
                        x=node['x'],
                        y=node['y'],
                        size=node['size'],
                        displayed_color=node['displayed_color'],
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
                # todo maybe set color, but affects performance
        current_node_idx += 1
        if len(active_nodes) > current_node_idx + 1:
            current_node = active_nodes[current_node_idx]
    print("end")

    return ret_graph


# def has_next(array, idx):
#     return len(array) > idx + 1


def calculate_probability(current_age, age):
    age_diff = abs(int(current_age) - int(age))
    age_probability = (age_diff * 2) / 100
    total_probability = age_probability + BASE_PROBABILITY
    if total_probability > 0.98:
        total_probability = 0.98
    return total_probability


def isGraphCompatibleLite(graph):  # checks random node attrs needed by alg, implement function checking all nodes
    try:
        random.sample(graph['nodes'], 1)[0]['attributes']['gender']
        random.sample(graph['nodes'], 1)[0]['attributes']['age']
        return True
    except KeyError:
        return False
