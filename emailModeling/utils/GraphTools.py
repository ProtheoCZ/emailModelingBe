import networkx as nx


HUB_THRESHOLD = 50


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
