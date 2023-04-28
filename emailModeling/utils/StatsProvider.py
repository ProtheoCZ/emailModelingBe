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
        depth += 1  #todo fix this, gives node count
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
            "is_tree": int(is_tree),
            "node_count": node_count,
            "is_hub_start": int(is_hub_start),
        }

        result_stats = {**result_stats, **children_stats}

        return result_stats


def get_stats(graph, root, graph_name, is_hub_start, run_id, sim_id):
    run_result = get_tree_stats(graph, root, graph_name, is_hub_start, run_id)
    diff = 6 - len(str(run_id))
    run_number = str(run_id)

    for i in range(diff):
        run_number = '0' + run_number

    with open(FULL_SIM_DIR + '/Sim_' + str(sim_id) + '/Run_' + run_number + '.json', 'w') as json_file:
        json.dump(run_result, json_file)


def get_sim_id(): # todo fix this only works for 1 digit id
    previous_runs = [file for file in os.listdir(FULL_SIM_DIR)]

    if len(previous_runs) == 0:
        sim_id = 0
    else:
        sim_id = int(previous_runs[-1][-1]) + 1
    return sim_id


def get_summary_stats(sim_id):
    path = FULL_SIM_DIR + '/Sim_' + str(sim_id) + '/'
    with open(path + '/Run_000001.json', 'r') as file:
        first_run = json.load(file)
        static_result = {
            "original_graph_name": first_run["original_graph_name"],
            "is_hub_start": first_run["is_hub_start"],
        }

    children_keys = [str(i) for i in range(RECORDED_CHILDREN_COUNT - 1)]
    children_keys.append(str(RECORDED_CHILDREN_COUNT - 1) + "+")

    sum_result = {
        "run_count": 0,
        "tree_count": 0,
        "avg_children_counts": get_children_count_empty_dict(),
        "non-tree_count": 0,
        "avg_triangles": 0,
        "avg_node_count": 0,

        "avg_depth": 0,
        "avg_max_children": 0
    }

    for filename in os.listdir(path):
        with open(path + filename, 'r') as file:
            run = json.load(file)
            sum_result["run_count"] += 1
            if run["is_tree"] == 1:
                sum_result["avg_depth"] += run["depth"]
                sum_result["avg_max_children"] += run["max_children"]
                for key in run["children_counts"]:
                    sum_result["avg_children_counts"][key] += run["children_counts"][key]

            else:
                sum_result["avg_triangles"] += run["triangles"]

            sum_result["avg_node_count"] += run["node_count"]

            if run["is_tree"] == 1:
                sum_result["tree_count"] += 1
            else:
                sum_result["non-tree_count"] += 1

            for key in run["children_counts"]:
                sum_result["avg_children_counts"][key] += run["children_counts"][key]

    sum_result = get_avg_stats(sum_result)
    sum_result = {**static_result, **sum_result}

    with open(path + 'Summary.json', 'w') as summary:
        json.dump(sum_result, summary)


def get_children_count_empty_dict():
    children_count_arr = [0 for _ in range(RECORDED_CHILDREN_COUNT)]
    children_keys = [str(i) for i in range(RECORDED_CHILDREN_COUNT - 1)]
    children_keys.append(str(RECORDED_CHILDREN_COUNT - 1) + "+")
    children_dict = {children_keys[i]: children_count_arr[i] for i in range(len(children_keys))}

    return children_dict


def get_avg_stats(sum_result):
    run_count = sum_result["run_count"]
    tree_count = sum_result["tree_count"]
    non_tree_count = sum_result["non-tree_count"]

    if tree_count > 0:
        sum_result["avg_depth"] = sum_result["avg_depth"]/tree_count
        sum_result["avg_max_children"] = sum_result["avg_max_children"]/tree_count
        sum_result["avg_node_count"] = sum_result["avg_node_count"]/tree_count

    for key in sum_result["avg_children_counts"]:
        sum_result["avg_children_counts"][key] = sum_result["avg_children_counts"][key]/run_count

    if non_tree_count > 0:
        sum_result["avg_triangles"] = sum_result["avg_triangles"]/non_tree_count

    return sum_result
