import json
import random

import networkx as nx


HUB_THRESHOLD = 50
POST_COLOR = 'rgb(0,255,0)'
RESPONSE_COLOR = 'rgb(0,0,255)'
START_COLOR = 'rgb(242,245,66)'
RESPONSE_EDGE_COLOR = 'rgb(0,0,0)'
GROUP_REPLY_COLOR = 'rgb(105,105,105)'
IGNORANT_COLOR = 'rgb(0,0,0)'
STIFLER_COLOR = 'rgb(128,0,128)'
SPREADER_COLOR = 'rgb(255,0,0)'


def get_hub_start(graph, n):  # n is the number of neighbors needed to be considered a hub
    while True:
        start_node_id = random.sample(graph.nodes, 1)[0]
        neighbors = [n for n in graph.neighbors(start_node_id)]
        if len(neighbors) >= n:
            return start_node_id


def order_tree(tree, root):
    if isinstance(tree, nx.Graph):
        tree = tree.copy()
        placed_nodes = []
        nx.set_node_attributes(tree, {root: {'x': -1, 'y': -1, 'size': 5}})
        placed_nodes.append(root)

        previous_gen = [root]

        y = 0
        while len(previous_gen) > 0:
            x = 0
            current_gen = []
            for parent in previous_gen:
                current_root = parent
                for neighbor in tree.neighbors(current_root):
                    if neighbor not in placed_nodes:
                        current_gen.append(neighbor)

            for node in current_gen:
                nx.set_node_attributes(tree, {node: {'x': x, 'y': y, 'size': 5}})
                placed_nodes.append(node)
                x += 1

            y += 1
            previous_gen = current_gen
    return tree


def add_node_to_graph(graph, node):
    if isinstance(graph, nx.Graph):
        graph.add_node(
            node['id'],
            x=node['x'],
            y=node['y'],
            size=node['size'],
            displayed_color=node['displayed_color'],
            label=node['label'],
            id=node['id']
        )


def treeify(graph, to_start=False):
    ret_graph = nx.Graph()
    start_node = None
    post_nodes = []
    for node in graph.nodes:
        displayed_color = graph.nodes[node]['displayed_color']
        if displayed_color == POST_COLOR:
            post_nodes.append(node)
        if displayed_color == START_COLOR:
            start_node = graph.nodes[node]
            post_nodes.append(node)

    add_node_to_graph(ret_graph, start_node)

    edge_id = 0
    for i in range(len(post_nodes) - 1):
        if to_start:
            shortest_path = nx.dijkstra_path(graph, post_nodes[i + 1], start_node['id'])
        else:
            shortest_path = nx.dijkstra_path(graph, post_nodes[i], post_nodes[i + 1])
        for idx, node in enumerate(shortest_path):
            add_node_to_graph(ret_graph, graph.nodes[node])
            if idx + 1 < len(shortest_path):
                neighbor = shortest_path[idx + 1]
                ret_graph.add_edge(
                    node,
                    neighbor,
                    displayed_color=RESPONSE_EDGE_COLOR,
                    size=1,
                    id=edge_id
                )
                edge_id += 1
    is_tree = nx.is_tree(ret_graph)
    print("is_tree = " + str(is_tree))
    # if is_tree:
    #     ret_graph = self.order_tree(ret_graph, start_node['id'])
    return ret_graph


def json_loader(json_graph_name):
    file = open('GraphData/' + json_graph_name)
    json_file = json.load(file)
    return json_file


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
