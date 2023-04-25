import random
import sympy as sy
import networkx as nx


class LnkAlg:
    def __init__(self, graph, discard_rate, back_rate, post_rate):
        self.lower_bound = 0.05
        self.upper_bound = 0.1
        self.interval_increase = 0.1
        self.exponent = -3 / 2
        self.integral_array = []
        self.values = []
        self.probabilities = []
        self.graph = nx.Graph  # remove this
        self.POST_COLOR = 'rgb(0,255,0)'
        self.RESPONSE_COLOR = 'rgb(0,0,255)'
        self.START_COLOR = 'rgb(242,245,66)'
        self.RESPONSE_EDGE_COLOR = 'rgb(255,0,0)'
        self.START_FOLDER = 'fullSimData6'
        self.ITERATION_COUNT = 1001

        if isinstance(graph, nx.Graph):
            self.graph = graph

            self.orig_graph = self.graph.copy()

        self.discard_rate = discard_rate  # 0.65, 0.5-0.75
        self.back_rate = back_rate  # 0.95
        self.post_rate = post_rate  # 0.22

        self.generate_t_probabilities()

    def f(self, x):
        return x ** self.exponent

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
        return int(10 * random.choices(self.values, weights=self.probabilities)[0])

    def getOnlyColoredNodes(self):
        ret_graph = nx.Graph()
        for node in self.graph.nodes:
            displayed_color = self.graph.nodes[node]['displayed_color']
            if displayed_color == self.POST_COLOR or displayed_color == self.RESPONSE_COLOR or displayed_color == self.START_COLOR:
                node_to_add = self.graph.nodes[node]
                ret_graph.add_node(
                    node_to_add['id'],
                    x=node_to_add['x'],
                    y=node_to_add['y'],
                    size=node_to_add['size'],
                    displayed_color=node_to_add['displayed_color'],
                    label=node_to_add['label'],
                    id=node_to_add['id']
                )
        i = 1
        for node in ret_graph:
            for neighbor in ret_graph:
                if self.graph.has_edge(node, neighbor) and node != neighbor and self.graph.get_edge_data(node, neighbor)['displayed_color'] == self.RESPONSE_EDGE_COLOR:
                    ret_graph.add_edge(
                        node,
                        neighbor,
                        displayed_color=self.RESPONSE_EDGE_COLOR,
                        size=1,
                        id=i
                    )
                    i += 1

        return ret_graph

    def treeify(self, graph):
        ret_graph = nx.Graph()
        start_node = None
        post_nodes = []
        for node in graph.nodes:
            displayed_color = graph.nodes[node]['displayed_color']
            if displayed_color == self.POST_COLOR:
                post_nodes.append(node)
            if displayed_color == self.START_COLOR:
                start_node = graph.nodes[node]

        self.add_node_to_graph(ret_graph, start_node)

        edge_id = 0
        for i in range(len(post_nodes) - 1):
            shortest_path = nx.dijkstra_path(graph, post_nodes[i], post_nodes[i+1])
            for idx, node in enumerate(shortest_path):
                self.add_node_to_graph(ret_graph, graph.nodes[node])
                if idx + 1 < len(shortest_path):
                    neighbor = shortest_path[idx+1]
                    ret_graph.add_edge(
                        node,
                        neighbor,
                        displayed_color=self.RESPONSE_EDGE_COLOR,
                        size=1,
                        id=edge_id
                    )
                    edge_id += 1
        is_tree = nx.is_tree(ret_graph)
        print("is_tree = " + str(is_tree))
        # if is_tree:
        #     ret_graph = self.order_tree(ret_graph, start_node['id'])
        return ret_graph

    def order_tree(self, tree, root):
        if isinstance(tree, nx.Graph):
            tree = tree.copy()
            placed_nodes = []
            nx.set_node_attributes(tree, {root: {'x': -1, 'y': -1, 'size': 5}})
            placed_nodes.append(root)

            previous_gen = [root]

            y = 0
            number_of_children = [0 for _ in range(10)]
            while len(previous_gen) > 0:
                x = 0
                current_gen = []
                for parent in previous_gen:
                    current_root = parent
                    children_count = 0
                    for neighbor in tree.neighbors(current_root):
                        if neighbor not in placed_nodes:
                            current_gen.append(neighbor)
                            children_count += 1

                    if children_count > len(number_of_children) - 1:
                        number_of_children[-1] += 1
                    else:
                        number_of_children[children_count] += 1

                for node in current_gen:
                    nx.set_node_attributes(tree, {node: {'x': x, 'y': y, 'size': 5}})
                    placed_nodes.append(node)
                    x += 1

                y += 1
                previous_gen = current_gen

            self.get_children_stats(number_of_children)
        return tree

    def get_children_stats(self, number_of_children, log_to_file=False):
        total = sum(number_of_children)
        for idx, n in enumerate(number_of_children):
            if log_to_file:
                pass  # todo logging to file
            else:
                print(str(n) + ' out of ' + str(total) + ' nodes had ' + str(idx) + ' children')  # todo add percentage

    def add_node_to_graph(self, graph, node):
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

    def get_avg_post_children(self, graph):
        if isinstance(graph, nx.Graph):
            val_arr = []
            for node in graph.nodes:
                if graph.nodes[node]['displayed_color'] == self.POST_COLOR:
                    neighbors = [n for n in graph.neighbors(node)]
                    number_of_posting_neighbors = 0
                    for neighbor in neighbors:
                        if graph.nodes[neighbor]['displayed_color'] == self.POST_COLOR:
                            number_of_posting_neighbors += 1
                    val_arr.append(number_of_posting_neighbors)

            non_zero_val_arr = [v for v in val_arr if v > 0]

            if len(val_arr) and len(non_zero_val_arr) > 0:
                print("average number of posting neighbors is: " + str(sum(val_arr) / len(val_arr)))
                print("average number non zero posting neighbors is: " + str(
                    sum(non_zero_val_arr) / len(non_zero_val_arr)))
                # return sum(val_arr)/len(val_arr)
            else:
                print("nobody responded!")

    def get_hub_start(self, n):  # n is the number of neighbors needed to be considered a hub
        graph_len = self.graph.number_of_nodes()
        while True:
            # start_node = self.graph.nodes[str(random.randint(1, graph_len))]
            start_node_id = random.sample(self.graph.nodes, 1)[0]
            neighbors = [n for n in self.graph.neighbors(start_node_id)]
            if len(neighbors) >= n:
                return self.graph.nodes[start_node_id]

    def run_alg(self):
        # start_node = random.sample(self.graph.nodes, 1)
        # start_node = self.graph.nodes[str(random.randint(1, self.graph.number_of_nodes()))]
        start_node = self.get_hub_start(50)  # todo for testing with hubs
        # start_node = self.graph.nodes['486']  # TODO for editedGraph, don't forget to remove !
        # start_node = self.graph.nodes['422']  # TODO for emaileuall, don't forget to remove !
        # start_node = self.graph.nodes['1']    # TODO for barabasi-albert testing, don't forget to remove !
        # start_node = self.graph.nodes['105']     # TODO for small_graph testing, don't forget to remove !
        # start_node = self.graph.nodes['122']

        ret_array = []

        active_nodes = [[] for _ in range(self.ITERATION_COUNT)]
        responders = []
        for node in self.graph.neighbors(start_node['id']):
            if random.random() - self.discard_rate >= 0:
                t = self.generate_t()
                nx.set_node_attributes(self.graph, {node: t}, name="t")
                active_nodes[t].append((start_node['id'], node))

        for i in range(self.ITERATION_COUNT):  # todo select better range
            for node_pair in active_nodes[i]:
                receiver = node_pair[1]
                sender = node_pair[0]

                attrs = {(sender, receiver): {'displayed_color': self.RESPONSE_EDGE_COLOR}}
                if random.random() - self.back_rate >= 0:
                    if random.random() <= self.post_rate:
                        self.graph.nodes[receiver]['displayed_color'] = self.POST_COLOR
                        responders.append(receiver)
                        nx.set_edge_attributes(self.graph, attrs)

                    else:
                        self.graph.nodes[receiver]['displayed_color'] = self.RESPONSE_COLOR
                        responders.append(receiver)
                        nx.set_edge_attributes(self.graph, attrs)

                    for neighbor in self.graph.neighbors(receiver):
                        if random.random() - self.discard_rate >= 0:
                            is_already_active = False

                            for node_array in active_nodes:
                                for active_node_pair in node_array:  # todo tohle je blbe po optimalizaci
                                    active_node = active_node_pair[1]
                                    if active_node == neighbor:
                                        is_already_active = True
                                        break

                            if not is_already_active:
                                t = self.generate_t()
                                nx.set_node_attributes(self.graph, {neighbor: t + i}, name="t")
                                active_nodes[t].append((receiver, neighbor))
            # print("responders len is " + str(len(responders)) + " and i is " + str(i))
            # print(responders)

            # if i % 1 == 0:
            self.graph.nodes[start_node['id']]['displayed_color'] = self.START_COLOR
            if i == 1000:
                # ret_array.append(self.graph)
                ret_graph = self.getOnlyColoredNodes()
                # self.get_avg_post_children(ret_graph)
                ret_array.append(ret_graph)

                ret_tree = self.treeify(ret_graph)
                ret_array.append(ret_tree)
                if nx.is_tree(ret_tree):
                    ordered_tree = self.order_tree(ret_tree, start_node['id'])
                    ret_array.append(ordered_tree)

        # for node in active_nodes:
        #     print(node)

        return ret_array

    def run_full_simulation(self, critical_len, n):
        # orig_back_rate = self.back_rate
        orig_post_rate = self.post_rate
        number_of_br_increases = round((1 - self.back_rate) * 100)
        number_of_pr_increases = round((0.35 - self.post_rate) * 100)
        graph_number = 1
        run_number = 1
        number_of_runs = n*number_of_pr_increases*number_of_br_increases
        for i in range(number_of_br_increases):
            self.post_rate = orig_post_rate
            self.back_rate += 0.01
            for j in range(number_of_pr_increases):
                for k in range(n):
                    results = self.run_alg()
                    graph = results[1]  # todo check which graph you actually want
                    if results[0].number_of_nodes() >= critical_len:
                        graph_name = self.START_FOLDER + "/graph_" + str(graph_number) + "_br_" + str(self.back_rate) + "_pr_" + str(self.post_rate) + ".gexf"
                        nx.write_gexf(graph, graph_name, version="1.2draft")
                        print("Graph run# " + str(run_number) + " exceeded critical length. Written as graph #" + str(graph_number))
                        graph_number += 1
                    print("run #" + str(run_number) + " of " + str(number_of_runs))
                    run_number += 1
                    self.graph = self.orig_graph.copy()

                self.post_rate += 0.01
