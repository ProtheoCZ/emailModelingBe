import networkx as nx


def order_tree(tree, root):  # todo clean children stats mess
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

        # Sp.get_children_stats(number_of_children)
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
