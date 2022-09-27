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
            self.start_node = self.graph.nodes['486']

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
        return 10*random.choices(self.values, weights=self.probabilities)[0]

    def run_alg(self):
        # TODO solve duplicate active nodes, color edges
        # put t as node param and check if "node in active_nodes"
        print("start node is " + self.start_node['id'])
        ret_array = []
        self.graph.nodes[self.start_node['id']]['displayed_color'] = 'rgb(242,245,66)'
        active_nodes = []  # array of tuples, (node,t)
        for node in self.graph.neighbors(self.start_node['id']):
            if random.random() - self.discard_rate >= 0:
                nx.set_node_attributes(self.graph, {node: self.generate_t()}, name="t")
                # active_nodes.append((node, self.generate_t()))
                active_nodes.append(node)

        for i in range(2000):  # select better range
            for node in active_nodes:
                # if i == node[1]:
                if i == self.graph.nodes[node]['t']:
                    if random.random() - self.back_rate >= 0:
                        if random.random() <= self.post_rate:
                            self.graph.nodes[node]['displayed_color'] = 'rgb(0,255,0)'
                        else:
                            self.graph.nodes[node]['displayed_color'] = 'rgb(0,0,255)'

                        for neighbor in self.graph.neighbors(node):
                            if random.random() - self.discard_rate >= 0:

                                is_already_active = False
                                for active_node in active_nodes:
                                    if active_node == neighbor:
                                        is_already_active = True
                                        break

                                if not is_already_active:
                                    nx.set_node_attributes(self.graph, {neighbor: self.generate_t()}, name="t")
                                    # active_nodes.append((neighbor, i + self.generate_t()))
                                    active_nodes.append(neighbor)
                # active_nodes.pop(0) # “collections.deque”, which has a “popleft” method which is O(1).

            if i % 100 == 0:
                ret_array.append(self.graph)

        for node in active_nodes:
            print(node)
        return ret_array
