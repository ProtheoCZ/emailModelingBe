import json
import random

import networkx as nx


def simulate_relatability(graph_name):
    json_graph = json_loader(graph_name)
    graph = json_to_nx(json_graph)
    age_relatability(graph)


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
            age=node['age'],
            gender=node['gender']
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
    start_node = graph.nodes[str(random.randint(1, graph.number_of_nodes()))]
    current_node = start_node
    print("end")

