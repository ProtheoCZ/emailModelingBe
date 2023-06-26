import os

import networkx as nx
import random
from ..utils import StatsProvider as Sp

NODE_COLOR = 'rgb(255,0,0)'
SIZE = 4
NUMBER_OF_GENERATIONS = 10000
children_probabilities = (0.0246, 0.9525, 0.0217, 0.0012)


# probabilities for individual children are
# 0 - 0.0246
# 1 - 0.9525
# 2 - 0.0217
# 3 - 0.0012
# 4+ - 0

def generate_tree(probabilities=children_probabilities):
    children = [i for i in range(len(probabilities))]
    # cumulative_children_probabilities = [0.0246, 0.9771, 0.9988, 1]
    graph = nx.Graph()
    current_node_id = 1
    graph.add_node(
        current_node_id,
        x=-1,
        y=-1,
        size=10,
        displayed_color='rgb(242,245,66)',
        label=current_node_id,
        id=current_node_id
    )
    current_generation = [graph.nodes[current_node_id]]
    current_node_id += 1
    i = 0
    number_of_branches = 0
    while len(current_generation) > 0 and i <= NUMBER_OF_GENERATIONS:
        i += 1
        next_generation = []
        for index, node in enumerate(current_generation):
            number_of_children = int(random.choices(children, weights=probabilities, k=1)[0])
            if number_of_children > 1:
                number_of_branches += 1
            if number_of_children == 0:
                number_of_branches -= 1
            for j in range(number_of_children):
                graph.add_node(
                    current_node_id,
                    x=index + len(next_generation),
                    y=i,
                    size=SIZE,
                    displayed_color=NODE_COLOR,
                    label=current_node_id,
                    id=current_node_id
                )
                current_node = graph.nodes[current_node_id]
                graph.add_edge(
                    node["id"],
                    current_node["id"],
                    displayed_color='rgb(0,0,0)',
                    size=1,
                    id=current_node_id
                )
                next_generation.append(current_node)
                current_node_id += 1
        current_generation = next_generation.copy()

    return graph


def full_gw_sim(run_count, export_stats=True):
    sim_id = Sp.get_sim_id()
    if export_stats:
        os.mkdir(Sp.FULL_SIM_DIR + '/Sim_' + str(sim_id))
    for i in range(run_count):
        tree = generate_tree()
        Sp.get_stats(tree,
                     1,
                     'Galton-Watson generated tree',
                     False,
                     i+1,
                     sim_id,
                     tree
                     )
        print("run #" + str(i + 1) + " of " + str(run_count))

    if export_stats:
        Sp.get_summary_stats(sim_id, "Galton Watson tree")
