import random
import sympy as sy
import networkx as nx


class LnkAlg:

    def __init__(self, graph, discard_rate, back_rate, post_rate):
        self.lower_bound = 0.05
        self.upper_bound = 0.1
        self.interval_increase = 0.1
        self.exponent = -3/2
        self.integral_array = []
        self.values = []
        self.probabilities = []
        self.graph = nx.Graph  # remove this

        if isinstance(graph, nx.Graph):
            self.graph = graph
            self.start_node = self.graph.nodes[str(random.randint(1, self.graph.number_of_nodes()))]
            self.start_node = self.graph.nodes['486']  # for editedGraph, don't forget to remove !
            self.start_node = self.graph.nodes['422']  # for emaileuall, don't forget to remove !

        self.discard_rate = discard_rate  # 0.65, 0.5-0.75
        self.back_rate = back_rate  # 0.95
        self.post_rate = post_rate  # 0.22

        self.generate_t_probabilities()

    def f(self, x):
        return x**self.exponent

    def generate_t_probabilities(self):
        x = sy.Symbol("x")
        print(sy.integrate(self.f(x), (x, 0.05, 0.1)))

        while self.upper_bound <= 20:  # 20
            interval_integral = sy.integrate(self.f(x), (x, self.lower_bound, self.upper_bound))

            self.integral_array.append([self.lower_bound, self.upper_bound, interval_integral])

            self.lower_bound = self.upper_bound
            self.upper_bound += self.interval_increase

        print(self.integral_array)

        for i in range(len(self.integral_array)):
            self.values.append(self.integral_array[i][1])
            self.probabilities.append(self.integral_array[i][2])

    def generate_t(self):  # returns int
        return int(10*random.choices(self.values, weights=self.probabilities)[0])

    def run_alg(self):
        # TODO color edges
        print("start node is " + self.start_node['id'])
        ret_array = []
        self.graph.nodes[self.start_node['id']]['displayed_color'] = 'rgb(242,245,66)'
        active_nodes = []  # array of nodes with t param, rewrite as tuple of nodes (sender,receiver with t param)
        responders = []
        for node in self.graph.neighbors(self.start_node['id']):
            if random.random() - self.discard_rate >= 0:
                nx.set_node_attributes(self.graph, {node: self.generate_t()}, name="t")
                active_nodes.append(node)
                # active_nodes.append(self.start_node,node)

        for i in range(2001):  # select better range
            for node in active_nodes:
                if i == self.graph.nodes[node]['t']:
                # if i == self.graph.nodes[node[1]]['t']:
                    if random.random() - self.back_rate >= 0:
                        if random.random() <= self.post_rate:
                            self.graph.nodes[node]['displayed_color'] = 'rgb(0,255,0)'
                            responders.append(node)
                        else:
                            self.graph.nodes[node]['displayed_color'] = 'rgb(0,0,255)'
                            responders.append(node)

                        for neighbor in self.graph.neighbors(node):
                            if random.random() - self.discard_rate >= 0:
                                is_already_active = False

                                for active_node in active_nodes:
                                    if active_node == neighbor:
                                    # if active_node[1] == neighbor:
                                        is_already_active = True
                                        break

                                if not is_already_active:
                                    nx.set_node_attributes(self.graph, {neighbor: self.generate_t() + i}, name="t")
                                    active_nodes.append(neighbor)
                                    # active_nodes.append(node, neighbor)
            print("responders len is " + str(len(responders)) + " and i is " + str(i))
            print(responders)

            # if i % 1 == 0:
            if i == 2000:
                ret_array.append(self.graph)

        # for node in active_nodes:
        #     print(node)

        return ret_array
