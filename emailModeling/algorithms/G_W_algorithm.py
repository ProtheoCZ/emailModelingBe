import networkx as nx
import random

NODE_COLOR = 'rgb(255,0,0)'
SIZE = 4
NUMBER_OF_GENERATIONS = 20
children_probabilities = [0.0246, 0.9525, 0.0217, 0.0012]
children = [i for i in range(len(children_probabilities))]


# probabilities for individual children are
# 0 - 0.0246
# 1 - 0.9525
# 2 - 0.0217
# 3 - 0.0012
# 4+ - 0
def generate_tree():
    # Todo fix node visual placement
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

    for i in range(NUMBER_OF_GENERATIONS):
        next_generation = []
        for node in current_generation:
            number_of_children = int(random.choices(children, weights=children_probabilities, k=1)[0])
            for j in range(number_of_children):
                graph.add_node(
                    current_node_id,
                    x=j,
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
