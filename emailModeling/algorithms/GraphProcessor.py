import json

import networkx as nx
from .L_NK_algorithm import LnkAlg
from .G_W_algorithm import generate_tree


class GraphProcessor:
    def __init__(self, json_graph_name):
        self.graph = None
        if json_graph_name is not None:
            self.json_graph_name = json_graph_name
            self.active_node = '1'
            self.json_to_networkx()

    def json_loader(self):
        file = open('GraphData/' + self.json_graph_name)
        json_file = json.load(file)
        return json_file

    def json_to_networkx(self):
        json_graph = self.json_loader()
        self.graph = nx.Graph()

        for node in json_graph['nodes']:
            self.graph.add_node(
                node['id'],
                x=node['x'],
                y=node['y'],
                size=node['size'],
                displayed_color=node['color'],
                label=node['label'],
                id=node['id']
            )

        for edge in json_graph['edges']:
            self.graph.add_edge(
                edge['source'],
                edge['target'],
                displayed_color=edge['color'],
                size=edge['size'],
                id=edge['id']
            )

    def networkx_to_json(self):
        ret_json = {
            "nodes": [],
            "edges": []
        }
        for node in self.graph.nodes:
            json_node = {
                "label": self.graph.nodes[node]["label"],
                "x": self.graph.nodes[node]["x"],
                "y": self.graph.nodes[node]["y"],
                "id": self.graph.nodes[node]["id"],
                "attributes": {},
                "color": self.graph.nodes[node]["displayed_color"],
                "size": self.graph.nodes[node]["size"]
            }
            ret_json["nodes"].append(json_node)

        for edge in self.graph.edges:
            json_edge = {
                "source": edge[0],
                "target": edge[1],
                "id": self.graph.edges[edge]["id"],
                "attributes": {},
                "color": self.graph.edges[edge]["displayed_color"],
                "size": self.graph.edges[edge]["size"],
            }
            ret_json["edges"].append(json_edge)

        return ret_json

    def process_graph_lnk(self):
        lnk = LnkAlg(self.graph, self.json_graph_name, 0.65, 0.86, 0.22)
        ret_networkx = lnk.run_alg(False)

        ret_json = {"graphs": [], "compatible": 1}

        for graph in ret_networkx:
            self.graph = graph
            ret_json["graphs"].append(self.networkx_to_json())

        return ret_json

    def process_full_lnk(self):
        lnk = LnkAlg(self.graph, self.json_graph_name, 0.65, 0.83, 0.22)
        lnk.run_full_simulation(1000, 3000, False, 0.84, 0.23, True)

    def generate_gw_tree(self):
        ret_json = {"graphs": [], "compatible": 1}
        self.graph = generate_tree()
        ret_json["graphs"].append(self.networkx_to_json())

        return ret_json
