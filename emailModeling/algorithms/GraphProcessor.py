import json
import random

import networkx as nx
from .L_NK_algorithm import LnkAlg


class GraphProcessor:
    def __init__(self, json_graph_name):

        self.graph = None
        self.json_graph_name = json_graph_name
        self.active_node = '1'
        self.json_to_networkx()

    def json_loader(self):
        # print(self.json_graph_name)
        file = open('GraphData/' + self.json_graph_name)
        json_file = json.load(file)
        return json_file

    def json_to_networkx(self):
        json_graph = self.json_loader()
        # print(json_graph.keys())
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

        # print('nodes=' + str(nx.number_of_nodes(self.graph)) + " edges=" + str(nx.number_of_edges(self.graph)))

    def networkx_to_json(self):
        ret_json = {
            "nodes": [],
            "edges": []
        }
        for node in self.graph.nodes:
            # print(node)
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
            # print(edge[0])
            # print(edge)
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

    def process_graph(self):
        # self.json_to_networkx()  uncomment if it breaks

        for node in self.graph.nodes:
            self.graph.nodes[node]['displayed_color'] = 'rgb(0,0,0)'

        # print(self.graph.nodes['1']['displayed_color'])

        ret_json = {"graphs": []}

        for i in range(50):
            if i % 10 == 0:
                ret_json["graphs"].append(self.networkx_to_json())

            # for node in nx.all_neighbors(self.graph, self.active_node):
            #     self.graph.nodes[node]['displayed_color'] = 'rgb(255,0,0)'
            #     self.active_node = self.graph.nodes[node]['id']

            self.graph.nodes[str(random.randint(1, 100))]['displayed_color'] = 'rgb(255,0,0)'

        return ret_json

    def process_graph_lnk(self):

        lnk = LnkAlg(self.graph, 0.65, 0.85, 0.22)
        ret_networkx = lnk.run_alg()

        ret_json = {"graphs": []}

        for graph in ret_networkx:
            self.graph = graph
            ret_json["graphs"].append(self.networkx_to_json())


        return ret_json



