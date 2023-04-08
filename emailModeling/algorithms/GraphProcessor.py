import json
import random
import sympy as sy
import pandas as pd

import networkx as nx
from .L_NK_algorithm import LnkAlg
from .G_W_algorithm import generate_tree


def get_fraction_of_nodes_with_one_child(graph):
    if isinstance(graph, nx.Graph):
        number_of_nodes = graph.number_of_nodes()
        number_of_nodes_with_one_child = 0

        for node in graph.nodes:
            if sum(1 for _ in graph.neighbors(node)) == 1:
                number_of_nodes_with_one_child += 1

        fraction = number_of_nodes_with_one_child / number_of_nodes
        print("fraction of 1 neighbor nodes is " + str(fraction))
        # return fraction


class GraphProcessor:
    def __init__(self, json_graph_name):
        self.graph = None
        if json_graph_name is not None:
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

        lnk = LnkAlg(self.graph, 0.65, 0.90, 0.22)
        ret_networkx = lnk.run_alg()
        self.get_expected_distribution()
        self.get_degree_distribution()  # todo consider to turn back on
        # get_fraction_of_nodes_with_one_child(ret_networkx[0]) #todo consider to turn back on

        ret_json = {"graphs": []}

        for graph in ret_networkx:
            self.graph = graph
            ret_json["graphs"].append(self.networkx_to_json())

        return ret_json

    def process_full_lnk(self):
        lnk = LnkAlg(self.graph, 0.65, 0.90, 0.20)
        lnk.run_full_simulation(200, 10)

    def generate_gw_tree(self):
        ret_json = {"graphs": []}
        self.graph = generate_tree()
        ret_json["graphs"].append(self.networkx_to_json())

        return ret_json

    def f(self, x, exponent):
        return x ** exponent

    def get_expected_distribution(self):
        x = sy.Symbol("x")

        exponent = -2
        integral_dict = {}

        for i in range(3):
            integral_dict["x^" + str(exponent - i)] = []
            i_sum = 0
            for j in range(10):
                integral = sy.integrate(self.f(x, exponent-i), (x, 1+j, 2+j))
                i_sum += integral
                integral_dict["x^" + str(exponent-i)].append([1+j, 2+j, integral])

            for k in range(10):
                integral_dict["x^" + str(exponent-i)][k][2] = integral_dict["x^" + str(exponent-i)][k][2]/i_sum
        df = pd.DataFrame(data=integral_dict)
        pd.options.display.float_format = '${:,.2f}'.format
        print(df)

    def get_degree_distribution(self):
        if isinstance(self.graph, nx.Graph):
            number_of_nodes = self.graph.number_of_nodes()
            degree_distribution = [0 for _ in range(number_of_nodes)]
            cumulative_degree_distribution = [0 for _ in range(number_of_nodes)]
            cumulative_percentage = 0
            for node in self.graph.nodes:
                number_of_neighbors = sum(1 for _ in nx.neighbors(self.graph, node))
                degree_distribution[number_of_neighbors] += 1
                cumulative_degree_distribution[number_of_neighbors] += 1

            for i in range(number_of_nodes):
                nodes_with_degree = degree_distribution[i]
                degree_percentage = nodes_with_degree/number_of_nodes * 100
                cumulative_percentage += degree_percentage
                if nodes_with_degree > 0:
                    print("degree " + str(i) + ": " + str(nodes_with_degree) + " nodes | chance " + str(degree_percentage) + "% "
                          + "cumulative " + str(cumulative_percentage) + "%" + "\n")
