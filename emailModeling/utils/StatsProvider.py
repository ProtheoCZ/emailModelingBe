import os

import networkx as nx
import json
from ..utils import GraphTools as Gt

RECORDED_CHILDREN_COUNT = 10
FULL_SIM_DIR = 'fullSimStats'
POST_COLOR = 'rgb(0,255,0)'
RESPONSE_COLOR = 'rgb(0,0,255)'
START_COLOR = 'rgb(242,245,66)'


def get_children_stats(graph, root):
    visited_nodes = [root]
    node_queue = [root]
    children_count_arr = [0 for _ in range(RECORDED_CHILDREN_COUNT)]
    max_children = 0
    current_parent = root

    while len(node_queue) > 0:
        current_parent = node_queue.pop(0)
        current_gen = [node for node in nx.neighbors(graph, current_parent) if node not in visited_nodes]
        children_count = len(current_gen)
        max_children = max(children_count, max_children)
        if children_count < RECORDED_CHILDREN_COUNT:
            children_count_arr[children_count] += 1
        else:
            children_count_arr[-1] += 1

        for node in current_gen:
            visited_nodes.append(node)
            node_queue.append(node)

    depth = len(nx.dijkstra_path(graph, root, current_parent))

    children_keys = [str(i) for i in range(RECORDED_CHILDREN_COUNT - 1)]
    children_keys.append(str(RECORDED_CHILDREN_COUNT - 1) + "+")

    children_dict = {children_keys[i]: children_count_arr[i] for i in range(len(children_keys))}
    result_stats = {
        "tree_result_stats": {
            "children_counts": children_dict,
            "depth": depth,
            "max_children": max_children
        }
    }

    return result_stats


def get_tree_stats(graph, root, is_hub_start):
    if isinstance(graph, nx.Graph):
        is_tree = nx.is_tree(graph)
        node_count = nx.number_of_nodes(graph)
        if is_tree:
            children_stats = get_children_stats(graph, root)
        else:
            triangles = nx.triangles(graph)
            triangle_count = 0
            for triangle in triangles:
                triangle_count += triangles[triangle]

            triangle_count = triangle_count / 3

            children_stats = {
                "tree_result_stats": {
                    "triangles": triangle_count
                }
            }

        result_stats = {
            "tree_result_stats": {
                "is_tree": int(is_tree),
                "node_count": node_count,
                "is_hub_start": int(is_hub_start)
            },
        }

        result_stats["tree_result_stats"] = {**result_stats["tree_result_stats"], **children_stats["tree_result_stats"]}

        return result_stats


def get_stats(tree, root, graph_name, is_hub_start, run_id, sim_id, graph):
    metadata = {
        "original_graph_name": graph_name,
        "run_id": run_id
    }
    run_tree_result = get_tree_stats(tree, root, is_hub_start)
    graph_stats = get_graph_stats(graph)
    run_result = {**metadata, **run_tree_result, **graph_stats}
    run_diff = 6 - len(str(run_id))
    sim_diff = 3 - len(str(sim_id))
    run_number = str(run_id)
    sim_number = str(sim_id)

    for i in range(run_diff):
        run_number = '0' + run_number

    for i in range(sim_diff):
        sim_number = '0' + sim_number

    with open(FULL_SIM_DIR + '/Sim_' + sim_number + '/Run_' + run_number + '.json', 'w') as json_file:
        json.dump(run_result, json_file)


def get_graph_stats(graph):
    if isinstance(graph, nx.Graph):
        node_count = graph.number_of_nodes()
        post_nodes = 0
        response_nodes = 0
        hub_count = 0
        avg_neighbors = 0

        for node in graph.nodes:
            color = graph.nodes[node]['displayed_color']
            neighbors_len = len([neighbor for neighbor in graph.neighbors(node)])

            if neighbors_len >= Gt.HUB_THRESHOLD:
                hub_count += 1

            avg_neighbors += neighbors_len

            if color == START_COLOR or color == POST_COLOR:
                post_nodes += 1

            if color == RESPONSE_COLOR:
                response_nodes += 1

        avg_neighbors = avg_neighbors / node_count

        ret_dict = {
            "full_graph_stats": {
                "node_count": node_count,
                "post_nodes": post_nodes,
                "response_nodes": response_nodes,
                "hub_count": hub_count,
                "avg_neighbors": avg_neighbors
            }
        }

        return ret_dict


def get_sim_id():
    previous_runs = [file for file in os.listdir(FULL_SIM_DIR)]

    if len(previous_runs) == 0:
        sim_id = '000'
    else:
        sim_id = str(int(previous_runs[-1][-3:]) + 1)
        sim_diff = 3 - len(str(sim_id))
        sim_number = str(sim_id)
        for i in range(sim_diff):
            sim_number = '0' + sim_number

        sim_id = sim_number

    return sim_id


def get_summary_stats(sim_id):
    path = FULL_SIM_DIR + '/Sim_' + str(sim_id) + '/'
    with open(path + '/Run_000001.json', 'r') as file:
        loaded_json = json.load(file)
        first_run = loaded_json["tree_result_stats"]
        static_result = {
            "original_graph_name": loaded_json["original_graph_name"],
            "is_hub_start": first_run["is_hub_start"],
        }

    children_keys = [str(i) for i in range(RECORDED_CHILDREN_COUNT - 1)]
    children_keys.append(str(RECORDED_CHILDREN_COUNT - 1) + "+")

    sum_tree_result = {
        "run_count": 0,
        "tree_count": 0,
        "avg_children_counts": get_children_count_empty_dict(),
        "non-tree_count": 0,
        "avg_triangles": 0,
        "avg_node_count": 0,

        "avg_depth": 0,
        "avg_max_children": 0
    }

    sum_graph_result = {
        "run_count": 0,
        "avg_node_count": 0,
        "avg_post_nodes": 0,
        "avg_response_nodes": 0,
        "avg_hub_count": 0,
        "avg_neighbors": 0
    }

    for filename in os.listdir(path):
        with open(path + filename, 'r') as file:
            file_json = json.load(file)
            tree_run = file_json["tree_result_stats"]
            graph_run = file_json["full_graph_stats"]

            # tree stats
            sum_tree_result["run_count"] += 1
            if tree_run["is_tree"] == 1:
                sum_tree_result["avg_depth"] += tree_run["depth"]
                sum_tree_result["avg_max_children"] += tree_run["max_children"]
                for key in tree_run["children_counts"]:
                    sum_tree_result["avg_children_counts"][key] += tree_run["children_counts"][key]

            else:
                sum_tree_result["avg_triangles"] += tree_run["triangles"]

            sum_tree_result["avg_node_count"] += tree_run["node_count"]

            if tree_run["is_tree"] == 1:
                sum_tree_result["tree_count"] += 1
            else:
                sum_tree_result["non-tree_count"] += 1

            # for key in tree_run["children_counts"]:
            #     sum_tree_result["avg_children_counts"][key] += tree_run["children_counts"][key]

            # graph stats

            sum_graph_result["run_count"] += 1
            sum_graph_result["avg_node_count"] += graph_run["node_count"]
            sum_graph_result["avg_post_nodes"] += graph_run["post_nodes"]
            sum_graph_result["avg_response_nodes"] += graph_run["response_nodes"]
            sum_graph_result["avg_hub_count"] += graph_run["hub_count"]
            sum_graph_result["avg_neighbors"] += graph_run["avg_neighbors"]

    sum_graph_result = get_avg_graph_stats(sum_graph_result)
    sum_tree_result = get_avg_tree_stats(sum_tree_result)

    result = {
        **static_result,
        "summary_tree_stats": sum_tree_result,
        "summary_graph_stats": sum_graph_result
    }

    with open(path + 'Summary.json', 'w') as summary:
        json.dump(result, summary)


def get_children_count_empty_dict():
    children_count_arr = [0 for _ in range(RECORDED_CHILDREN_COUNT)]
    children_keys = [str(i) for i in range(RECORDED_CHILDREN_COUNT - 1)]
    children_keys.append(str(RECORDED_CHILDREN_COUNT - 1) + "+")
    children_dict = {children_keys[i]: children_count_arr[i] for i in range(len(children_keys))}

    return children_dict


def get_avg_graph_stats(sum_graph_result):
    run_count = sum_graph_result["run_count"]
    sum_graph_result["avg_node_count"] = sum_graph_result["avg_node_count"] / run_count
    sum_graph_result["avg_post_nodes"] = sum_graph_result["avg_post_nodes"] / run_count
    sum_graph_result["avg_response_nodes"] = sum_graph_result["avg_response_nodes"] / run_count
    sum_graph_result["avg_hub_count"] = sum_graph_result["avg_hub_count"] / run_count
    sum_graph_result["avg_neighbors"] = sum_graph_result["avg_neighbors"] / run_count

    return sum_graph_result


def get_avg_tree_stats(sum_result):
    run_count = sum_result["run_count"]
    tree_count = sum_result["tree_count"]
    non_tree_count = sum_result["non-tree_count"]

    if tree_count > 0:
        sum_result["avg_depth"] = sum_result["avg_depth"] / tree_count
        sum_result["avg_max_children"] = sum_result["avg_max_children"] / tree_count
        sum_result["avg_node_count"] = sum_result["avg_node_count"] / tree_count

    for key in sum_result["avg_children_counts"]:
        sum_result["avg_children_counts"][key] = sum_result["avg_children_counts"][key] / run_count

    if non_tree_count > 0:
        sum_result["avg_triangles"] = sum_result["avg_triangles"] / non_tree_count

    return sum_result
