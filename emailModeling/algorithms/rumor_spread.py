import json
import os
import random

import networkx as nx

from ..utils import GraphTools as Gt
from ..utils import StatsProvider as Sp

SPREADER = 'spreader'
STIFLER = 'stifler'
IGNORANT = 'ignorant'
OPPONENT = 'opponent'
NEUTRAL = 'neutral'
SUPPORTER = 'supporter'


# When a spreader contacts another spreader or a stifler the initiating spreader becomes a stifler at a rate alfa.
# Whenever a spreader contacts an ignorant, the ignorant becomes a spreader at a rate lambda.
# Individuals may also cease spreading a rumour spontaneously (i.e., without the need for any contact) at a rate delta.


def simulate_rumor_spread(graph_name):
    ret_json = {"graphs": [], "compatible": 0}
    json_graph = Gt.json_loader(graph_name)

    if isGraphCompatible(json_graph):
        graph = json_to_nx(json_graph)
        ret_graphs = rumor_spread(graph, True, 0.75, 1)
        for graph in ret_graphs:
            ret_json["graphs"].append(Gt.nx_to_json(graph))
        ret_json["compatible"] = 1

    return ret_json


def isGraphCompatible(graph):
    try:
        random.sample(graph['nodes'], 1)[0]['population_group']
        return True
    except KeyError:
        return False


def json_to_nx(json_graph):
    graph = nx.Graph()

    for node in json_graph['nodes']:
        graph.add_node(
            node['id'],
            x=node['x'],
            y=node['y'],
            size=node['size'],
            displayed_color=node['color'],
            label=node['label'],
            id=node['id'],
            population_group=node['population_group'],
            rumor_group=IGNORANT
        )

    for edge in json_graph['edges']:
        graph.add_edge(
            edge['source'],
            edge['target'],
            displayed_color=edge['color'],
            size=edge['size'],
            id=edge['id']
        )

    return graph


def rumor_spread(graph,
                 is_hub_start: bool = False,
                 cessation_chance=0.5,
                 spreader_to_stifler_chance=0.5,
                 start_node_id=None):
    if start_node_id is None:
        if is_hub_start:
            start_node_id = Gt.get_hub_start(graph, Gt.HUB_THRESHOLD)
        else:
            start_node_id = random.sample(graph.nodes, 1)[0]

    ret_graph = nx.Graph()
    start_node = graph.nodes[start_node_id]
    start_node['rumor_group'] = SPREADER
    ret_graph.add_node(
        start_node_id,
        x=start_node['x'],
        y=start_node['y'],
        size=start_node['size'],
        displayed_color=start_node['displayed_color'],
        label=start_node['label'],
        id=start_node['id'],
        population_group=start_node['population_group'],
        rumor_group=start_node['rumor_group']
    )

    queue = []  # (sender, receiver)
    current_edge_id = 1

    for neighbor in graph.neighbors(start_node_id):
        convert_ignorant(start_node_id, neighbor, graph, queue, ret_graph, current_edge_id)
        current_edge_id += 1

    while len(queue) > 0:
        current_node_pair = queue.pop(0)
        current_node_id = current_node_pair[1]

        for neighbor in graph.neighbors(current_node_id):
            neighbor_rumor_group = graph.nodes[neighbor]['rumor_group']

            if random.random() > cessation_chance:
                if neighbor_rumor_group == IGNORANT:
                    convert_ignorant(current_node_id, neighbor, graph, queue, ret_graph, current_edge_id)
                    current_edge_id += 1
                elif neighbor_rumor_group == SPREADER or neighbor_rumor_group == STIFLER:
                    if random.random() < spreader_to_stifler_chance:
                        graph.nodes[current_node_id]['rumor_group'] = STIFLER
                        ret_graph.nodes[current_node_id]['rumor_group'] = STIFLER
                        break

                    elif neighbor_rumor_group == SPREADER:
                        queue.append((current_node_id, neighbor))

    assign_visual_colors(graph)
    assign_visual_colors(ret_graph)
    ret_graphs = [graph, ret_graph]

    return ret_graphs


def assign_visual_colors(graph):
    for node in graph.nodes:
        rumor_group = graph.nodes[node]['rumor_group']
        if rumor_group == SPREADER:
            graph.nodes[node]['displayed_color'] = Gt.SPREADER_COLOR
        elif rumor_group == STIFLER:
            graph.nodes[node]['displayed_color'] = Gt.STIFLER_COLOR
        elif rumor_group == IGNORANT:
            graph.nodes[node]['displayed_color'] = Gt.IGNORANT_COLOR

    return graph


# Whenever a spreader contacts an ignorant, the ignorant becomes a spreader at a rate lambda.
def get_ignorant_to_spreader_chance(receiver_node):
    if receiver_node['population_group'] == OPPONENT:
        chance = get_opponent_to_spreader_conversion_chance()

    elif receiver_node['population_group'] == NEUTRAL:
        chance = get_neutral_to_spreader_conversion_chance()

    elif receiver_node['population_group'] == SUPPORTER:
        chance = get_supporter_to_spreader_conversion_chance()

    else:
        raise Exception("Population group not recognized")

    return chance


def convert_ignorant(current_node_id, neighbor_id, graph, queue, ret_graph, current_edge_id):
    neighbor_node = graph.nodes[neighbor_id]

    lambda_chance = get_ignorant_to_spreader_chance(neighbor_node)

    if random.random() < lambda_chance:
        neighbor_node['rumor_group'] = SPREADER
        queue.append((current_node_id, neighbor_id))
        ret_graph.add_node(
            neighbor_id,
            x=neighbor_node['x'],
            y=neighbor_node['y'],
            size=neighbor_node['size'],
            displayed_color=neighbor_node['displayed_color'],
            label=neighbor_node['label'],
            id=neighbor_node['id'],
            population_group=neighbor_node['population_group'],
            rumor_group=neighbor_node['rumor_group']
        )

        ret_graph.add_edge(
            current_node_id,
            neighbor_id,
            displayed_color=Gt.RESPONSE_EDGE_COLOR,
            size=1,
            id=current_edge_id
        )


def run_full_rumor_spread(graph_name,
                          run_count,
                          is_hub_start: bool,
                          spreader_to_stifler_increase=0,
                          cessation_increase=0,
                          export_stats=True,
                          initial_cessation_chance=0,
                          initial_spreader_to_stifler_chance=0):
    json_graph = Gt.json_loader(graph_name)

    if isGraphCompatible(json_graph):
        sim_id = Sp.get_sim_id()
        if export_stats:
            os.mkdir(Sp.FULL_SIM_DIR + '/Sim_' + str(sim_id))

        graph = json_to_nx(json_graph)

        cessation_chance = initial_cessation_chance
        spreader_to_stifler_chance = initial_spreader_to_stifler_chance

        # cessation_runs = int(round((1 / cessation_increase) + 1))
        cessation_runs = 10
        # spreader_to_stifler_runs = int(round((1 / spreader_to_stifler_increase) + 1))
        spreader_to_stifler_runs = 10

        run_number = 1


        for i in range(run_count):
            for j in range(cessation_runs):
                for k in range(spreader_to_stifler_runs):
                    if is_hub_start:
                        start_node_id = Gt.get_hub_start(graph, Gt.HUB_THRESHOLD)
                    else:
                        start_node_id = random.sample(graph.nodes, 1)[0]
                    graphs = rumor_spread(graph.copy(),
                                          is_hub_start,
                                          cessation_chance,
                                          spreader_to_stifler_chance,
                                          start_node_id)

                    if export_stats:
                        Sp.get_stats(None,
                                     start_node_id,
                                     graph_name,
                                     is_hub_start,
                                     run_number,
                                     sim_id,
                                     graphs[1]
                                     )

                    print(
                        "run #" + str(run_number) + " of " + str(run_count * cessation_runs * spreader_to_stifler_runs))
                    spreader_to_stifler_chance += spreader_to_stifler_increase
                    run_number += 1
                cessation_chance += cessation_increase

        if export_stats:
            Sp.get_summary_stats(sim_id, 'rumor relatability', 1000, False)
    else:
        print("Graph is not compatible with the model")


def get_run_params(config_path):
    with open(config_path) as config_file:
        json_file = json.load(config_file)
        cessation_runs = round((json_file["cessation_stop"] - json_file["cessation_start"])/0.1) + 1
        spreader_to_stifler_runs = round((json_file["spreader_to_stifler_stop"] - json_file["spreader_to_stifler_start"])/0.1) + 1

        return {"cessation_start": json_file["cessation_start"],
                "cessation_runs": cessation_runs,
                "spreader_to_stifler_start": json_file["spreader_to_stifler_start"],
                "spreader_to_stifler_runs": spreader_to_stifler_runs}


def run_full_rumor_spread_with_param_scaling(graph_name,
                                             run_count,
                                             is_hub_start: bool
                                             ):


    # cessation_chance = 0
    # spreader_to_stifler_chance = 0
    run_params = get_run_params('c:/Users/Tomas/PycharmProjects/emailModelingBe/emailModeling/rumour_spread_limits.json')

    cessation_chance = run_params["cessation_start"]
    spreader_to_stifler_chance = run_params["spreader_to_stifler_start"]

    cessation_increase = 0.1
    spreader_to_stifler_increase = 0.1

    # cessation_runs = int(1/cessation_increase) + 1
    # spreader_to_stifler_runs = int(1/spreader_to_stifler_increase) + 1

    cessation_runs = run_params["cessation_runs"]
    spreader_to_stifler_runs = run_params["spreader_to_stifler_runs"]

    for i in range(cessation_runs):
        for j in range(spreader_to_stifler_runs):
            run_full_rumor_spread(graph_name,
                                  run_count,
                                  is_hub_start,
                                  initial_cessation_chance=cessation_chance,
                                  initial_spreader_to_stifler_chance=spreader_to_stifler_chance,
                                  )

            spreader_to_stifler_chance += spreader_to_stifler_increase
        cessation_chance += cessation_increase


# source of reaction numbers
# https://web.archive.org/web/20230621082805/https://www.irozhlas.cz/zpravy-domov/spolecnost-neduvery-serial-dezinformace-vyzkum-skupiny-seznam_2306120500_pik

def get_opponent_to_spreader_conversion_chance():
    strong_opponent_weight = 17
    average_opponent_weight = 20
    weak_opponent_weight = 17

    weights = [strong_opponent_weight, average_opponent_weight, weak_opponent_weight]

    strong_opponent_reactions = [0.73, 0.13, 0.05, 0.06, 0.03, 0.00]
    average_opponent_reactions = [0.44, 0.30, 0.11, 0.08, 0.06, 0.01]
    weak_opponent_reactions = [0.29, 0.18, 0.11, 0.34, 0.08, 0.00]

    strong_opponent_conversion_chance = strong_opponent_reactions[-1] \
        + strong_opponent_reactions[-2]/2

    average_opponent_conversion_chance = average_opponent_reactions[-1] \
        + average_opponent_reactions[-2]/2

    weak_opponent_conversion_chance = weak_opponent_reactions[-1] \
        + weak_opponent_reactions[-2]/2

    conversion_chances = [strong_opponent_conversion_chance,
                          average_opponent_conversion_chance,
                          weak_opponent_conversion_chance]

    return random.choices(conversion_chances, weights=weights, k=1)[0]


def get_neutral_to_spreader_conversion_chance():
    apathetic_weight = 6
    there_is_something_to_it_weight = 13

    weights = [apathetic_weight, there_is_something_to_it_weight]

    apathetic_reactions = [0.05, 0.07, 0.10, 0.72, 0.05, 0.01]
    there_is_something_to_it_reactions = [0.12, 0.37, 0.25, 0.11, 0.14, 0.02]

    apathetic_conversion_chance = apathetic_reactions[-1] \
        + apathetic_reactions[-2]/2

    there_is_something_to_it_conversion_chance = there_is_something_to_it_reactions[-1] \
        + there_is_something_to_it_reactions[-2]/2

    conversion_chances = [apathetic_conversion_chance, there_is_something_to_it_conversion_chance]

    return random.choices(conversion_chances, weights=weights, k=1)[0]


def get_supporter_to_spreader_conversion_chance():
    weak_covid_supporter_weight = 12
    weak_migration_supporter_weight = 10
    strong_supporter_weight = 6

    weights = [weak_covid_supporter_weight, weak_migration_supporter_weight, strong_supporter_weight]

    weak_covid_supporter_reactions = [0.08, 0.10, 0.18, 0.30, 0.23, 0.13]
    weak_migration_supporter_reactions = [0.28, 0.16, 0.16, 0.08, 0.16, 0.16]
    strong_supporter_reactions = [0.02, 0.06, 0.14, 0.09, 0.19, 0.50]

    weak_covid_supporter_conversion_chance = weak_covid_supporter_reactions[-1] \
        + weak_covid_supporter_reactions[-2]/2

    weak_migration_supporter_conversion_chance = weak_migration_supporter_reactions[-1] \
        + weak_migration_supporter_reactions[-2]/2

    strong_supporter_conversion_chance = strong_supporter_reactions[-1] \
        + strong_supporter_reactions[-2]/2

    conversion_chances = [weak_covid_supporter_conversion_chance,
                          weak_migration_supporter_conversion_chance,
                          strong_supporter_conversion_chance]

    return random.choices(conversion_chances, weights=weights)[0]
