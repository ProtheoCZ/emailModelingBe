import json
import os
import random
import sympy as sy
import networkx as nx

from ..utils import GraphTools as Gt
from ..utils import StatsProvider as Sp


class LnkAlg:
    def __init__(self, graph, graph_name, discard_rate, back_rate, post_rate):
        self.start_node = None
        self.lower_bound = 0.3
        self.upper_bound = 0.4
        self.interval_increase = 0.1
        self.exponent = -3 / 2
        self.integral_array = []
        self.values = []
        self.probabilities = []
        self.graph = nx.Graph  # remove this
        self.graph_name = graph_name
        self.START_FOLDER = 'fullSimData'
        self.IDLE_CUTOFF = 200   # depends on time distribution

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
        print("calculating time distribution...")

        while self.upper_bound <= 20:  # 20
            interval_integral = sy.integrate(self.f(x), (x, self.lower_bound, self.upper_bound))

            self.integral_array.append([self.lower_bound, self.upper_bound, interval_integral])

            self.lower_bound = self.upper_bound
            self.upper_bound += self.interval_increase

        for i in range(len(self.integral_array)):
            self.values.append(self.integral_array[i][1])
            self.probabilities.append(self.integral_array[i][2])

        print("time distribution calculated")

    def generate_t(self):  # returns int
        return int(10 * random.choices(self.values, weights=self.probabilities)[0])

    def run_alg(self, is_hub_start):
        if is_hub_start:
            self.start_node = self.graph.nodes[Gt.get_largest_hub(self.graph)]
        else:
            self.start_node = self.graph.nodes[random.sample(self.graph.nodes, 1)[0]]

        last_activity_time = 0
        ret_array = []
        ret_graph_with_group_reply = nx.Graph()
        ret_graph_with_group_reply_edge_id = 1
        Gt.add_node_to_graph(ret_graph_with_group_reply, self.start_node)

        ret_graph_responders = nx.Graph()
        ret_graph_responders_edge_id = 1
        Gt.add_node_to_graph(ret_graph_responders, self.start_node)

        active_nodes = [[] for _ in range(1000)]
        responders = []
        for node in self.graph.neighbors(self.start_node['id']):
            if random.random() - self.discard_rate >= 0:
                t = self.generate_t()
                nx.set_node_attributes(self.graph, {node: t}, name="t")
                active_nodes[t].append((self.start_node['id'], node))

        i = 0
        while last_activity_time < self.IDLE_CUTOFF:
            if len(active_nodes) - i < 500:
                active_nodes.extend([[] for _ in range(1000)])

            if not active_nodes[i]:
                last_activity_time += 1
            else:
                last_activity_time = 0

            for node_pair in active_nodes[i]:
                receiver = node_pair[1]
                sender = node_pair[0]
                receiver_node = self.graph.nodes[receiver]
                attrs = {(sender, receiver): {'displayed_color': Gt.RESPONSE_EDGE_COLOR}}
                if random.random() - self.back_rate >= 0:
                    if random.random() <= self.post_rate:
                        receiver_node['displayed_color'] = Gt.POST_COLOR
                    else:
                        self.graph.nodes[receiver]['displayed_color'] = Gt.RESPONSE_COLOR

                    responders.append(receiver)
                    nx.set_edge_attributes(self.graph, attrs)
                    Gt.add_node_to_graph(ret_graph_with_group_reply, receiver_node)
                    ret_graph_with_group_reply.add_edge(sender,
                                                        receiver,
                                                        displayed_color=Gt.RESPONSE_EDGE_COLOR,
                                                        size=1,
                                                        id=ret_graph_with_group_reply_edge_id
                                                        )
                    ret_graph_with_group_reply_edge_id += 1

                    Gt.add_node_to_graph(ret_graph_responders, receiver_node)
                    ret_graph_responders.add_edge(sender,
                                                  receiver,
                                                  displayed_color=Gt.RESPONSE_EDGE_COLOR,
                                                  size=1,
                                                  id=ret_graph_responders_edge_id
                                                  )
                    ret_graph_responders_edge_id += 1

                    for neighbor in self.graph.neighbors(receiver):
                        if random.random() - self.discard_rate >= 0:
                            is_already_active = False

                            for node_array in active_nodes:
                                for active_node_pair in node_array:
                                    active_node = active_node_pair[1]
                                    if active_node == neighbor:
                                        is_already_active = True
                                        break

                            if not is_already_active:
                                t = self.generate_t()
                                nx.set_node_attributes(self.graph, {neighbor: t + i}, name="t")
                                active_nodes[t].append((receiver, neighbor))

                else:
                    self.graph.nodes[receiver]['displayed_color'] = Gt.GROUP_REPLY_COLOR
                    Gt.add_node_to_graph(ret_graph_with_group_reply, receiver_node)
                    ret_graph_with_group_reply.add_edge(sender,
                                                        receiver,
                                                        displayed_color=Gt.RESPONSE_EDGE_COLOR,
                                                        size=1,
                                                        id=ret_graph_with_group_reply_edge_id)
                    ret_graph_with_group_reply_edge_id += 1

            i += 1

        self.graph.nodes[self.start_node['id']]['displayed_color'] = Gt.START_COLOR
        ret_graph_with_group_reply.nodes[self.start_node['id']]['displayed_color'] = Gt.START_COLOR
        ret_graph_responders.nodes[self.start_node['id']]['displayed_color'] = Gt.START_COLOR

        ret_array.append(ret_graph_responders)
        ret_array.append(ret_graph_with_group_reply)
        print('number of nodes forwarding email is ' + str(nx.number_of_nodes(ret_graph_responders)))

        number_of_interacting_nodes = nx.number_of_nodes(ret_graph_with_group_reply)
        print('number of nodes responding to email is ' + str(number_of_interacting_nodes))

        ret_tree = Gt.treeify(ret_graph_responders, to_start=True)
        ret_array.append(ret_tree)
        ordered_tree = None
        if nx.is_tree(ret_tree):
            ordered_tree = Gt.order_tree(ret_tree, self.start_node['id'])
            ret_array.append(ordered_tree)

        if 2442 <= number_of_interacting_nodes:
            with open(self.START_FOLDER + '/graph_with_group_reply.json', 'w') as f:
                json.dump(Gt.nx_to_json(ret_graph_with_group_reply), f)

            with open(self.START_FOLDER + '/graph_responders.json', 'w') as f2:
                json.dump(Gt.nx_to_json(ret_graph_responders), f2)

            with open(self.START_FOLDER + '/tree.json', 'w') as f3:
                json.dump(Gt.nx_to_json(ret_tree), f3)

            if nx.is_tree(ret_tree) and ordered_tree is not None:
                with open(self.START_FOLDER + '/ordered_tree.json', 'w') as f4:
                    json.dump(Gt.nx_to_json(ordered_tree), f4)

        return ret_array

    def run_full_simulation(self,
                            crit_len,
                            n,
                            is_hub_start: bool,
                            max_back_rate,
                            max_post_rate,
                            export_results=False,
                            export_stats=True
                            ):
        sim_id = Sp.get_sim_id()
        if export_stats:
            os.mkdir(Sp.FULL_SIM_DIR + '/Sim_' + str(sim_id))
        orig_post_rate = self.post_rate
        number_of_br_increases = round((max_back_rate - self.back_rate) * 100)
        number_of_pr_increases = round((max_post_rate - self.post_rate) * 100)
        graph_number = 1
        run_number = 1
        number_of_runs = n * number_of_pr_increases * number_of_br_increases
        for i in range(number_of_br_increases):
            self.post_rate = orig_post_rate
            self.back_rate += 0.01
            for j in range(number_of_pr_increases):
                for k in range(n):
                    results = self.run_alg(is_hub_start)
                    tree = results[2]
                    if results[0].number_of_nodes() >= crit_len and export_results:
                        graph_name = self.START_FOLDER \
                                     + "/sim_" + str(sim_id) + "_" \
                                     + "graph_" + str(graph_number) \
                                     + "_br_" + str(self.back_rate) \
                                     + "_pr_" + str(self.post_rate) \
                                     + ".gexf"
                        nx.write_gexf(tree, graph_name, version="1.2draft")
                        print("Graph run# "
                              + str(run_number)
                              + " exceeded critical length. Written as graph #"
                              + str(graph_number))
                        graph_number += 1

                    if export_stats:
                        graph = results[0]
                        graph_with_back_rate = results[1]
                        Sp.get_stats(tree,
                                     self.start_node['id'],
                                     self.graph_name,
                                     is_hub_start,
                                     run_number,
                                     sim_id,
                                     graph,
                                     # graph_with_back_rate,
                                     graph_with_back_rate
                                     )

                    print("run #" + str(run_number) + " of " + str(number_of_runs))
                    run_number += 1
                    self.graph = self.orig_graph.copy()

                self.post_rate += 0.01
        if export_stats:
            Sp.get_summary_stats(sim_id, "Lnk")
