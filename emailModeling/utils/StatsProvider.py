import os

import networkx as nx
import json

RECORDED_CHILDREN_COUNT = 10
FULL_SIM_DIR = 'fullSimStats'


# def get_children_stats(number_of_children, log_to_file=False):
#     total = sum(number_of_children)
#     for idx, n in enumerate(number_of_children):
#         if log_to_file:
#             pass  # todo logging to file
#         elif idx == len(number_of_children) - 1:
#             print(str(n) + ' out of ' + str(total) + ' nodes had ' + str(idx) + '+ children')
#         else:
#             print(str(n) + ' out of ' + str(total) + ' nodes had ' + str(idx) + ' children')  # todo add percentage


def get_children_stats(graph, root):
    visited_nodes = [root]
    node_queue = [root]
    children_count_arr = [0 for _ in range(RECORDED_CHILDREN_COUNT)]
    depth = 0
    max_children = 0

    while len(node_queue) > 0:
        current_parent = node_queue.pop(0)
        current_gen = [node for node in nx.neighbors(graph, current_parent) if node not in visited_nodes]
        depth += 1
        children_count = len(current_gen)
        max_children = max(children_count, children_count)
        if children_count <= RECORDED_CHILDREN_COUNT:
            children_count_arr[children_count] += 1
        else:
            children_count_arr[-1] += 1

        for node in current_gen:
            visited_nodes.append(node)
            node_queue.append(node)

    children_keys = [str(i) for i in range(RECORDED_CHILDREN_COUNT-1)]
    children_keys.append(str(RECORDED_CHILDREN_COUNT - 1) + "+")

    children_dict = {children_keys[i]: children_count_arr[i] for i in range(len(children_keys))}
    result_stats = {
        "children_counts": children_dict,
        "depth": depth,
        "max_children": max_children
    }

    return result_stats


def get_tree_stats(graph, root, graph_name, is_hub_start, run_id):
    if isinstance(graph, nx.Graph):
        is_tree = nx.is_tree(graph)
        node_count = nx.number_of_nodes(graph)
        if is_tree:
            children_stats = get_children_stats(graph, root)
        else:
            children_stats = {"triangles": nx.triangles(graph)}

        result_stats = {
            "original_graph_name": graph_name,
            "run_id": run_id,
            "result_is_tree": is_tree,
            "node_count": node_count,
            "is_hub_start": is_hub_start,
        }

        result_stats = {**result_stats, **children_stats}

        return result_stats


def get_stats(graph, root, graph_name, is_hub_start, run_id, sim_id):
    run_result = get_tree_stats(graph, root, graph_name, is_hub_start, run_id)
    with open(FULL_SIM_DIR + '/FullSimRun' + str(sim_id), 'w') as json_file:
        json.dump(run_result, json_file)


def get_sim_id():
    previous_runs = [file for file in os.listdir(FULL_SIM_DIR)]

    if len(previous_runs) == 0:
        sim_id = 0
    else:
        sim_id = int(previous_runs[-1][-1]) + 1
    return sim_id
