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

TIME_EVOLUTION_GRAPH_FOLDER = 'rumourTimeEvolution/TimeEvolution/'


# When a spreader contacts another spreader or a stifler the initiating spreader becomes a stifler at a rate alfa.
# Whenever a spreader contacts an ignorant, the ignorant becomes a spreader at a rate lambda.
# Individuals may also cease spreading a rumour spontaneously (i.e., without the need for any contact) at a rate delta.


def simulate_rumor_spread(graph_name):
    ret_json = {"graphs": [], "compatible": 0}
    json_graph = Gt.json_loader(graph_name)

    if isGraphCompatible(json_graph):
        graph = json_to_nx(json_graph)
        ret_graphs = rumor_spread(graph, False, 0.02, 0.16)
        for graph in ret_graphs:
            ret_json["graphs"].append(Gt.nx_to_json(graph))
        ret_json["compatible"] = 1

    return ret_json


def isGraphCompatible(graph):  # fast but not 100% accurate
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
            start_node_id = Gt.get_largest_hub(graph)
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

    current_edge_id = 1
    spreaders = {start_node_id}
    for neighbor in graph.neighbors(start_node_id):
        convert_ignorant(start_node_id, neighbor, graph, spreaders, ret_graph, current_edge_id)
        current_edge_id += 1

    stiflers = set()
    spreader_lens = [len(spreaders)]
    stifler_lens = [len(stiflers)]

    while len(spreaders) > 0:
        current_node_id = random.sample(spreaders, 1)[0]

        if random.random() > cessation_chance:
            neighbors = [n for n in graph.neighbors(current_node_id)]
            neighbor = random.sample(neighbors, 1)[0]

            if graph.nodes[current_node_id]['rumor_group'] == SPREADER:
                neighbor_rumor_group = graph.nodes[neighbor]['rumor_group']

                if neighbor_rumor_group == IGNORANT:
                    convert_ignorant(current_node_id, neighbor, graph, spreaders, ret_graph, current_edge_id)
                    current_edge_id += 1

                elif neighbor_rumor_group == SPREADER or neighbor_rumor_group == STIFLER:
                    if random.random() <= spreader_to_stifler_chance:
                        graph.nodes[current_node_id]['rumor_group'] = STIFLER
                        ret_graph.nodes[current_node_id]['rumor_group'] = STIFLER
                        spreaders.remove(current_node_id)
                        stiflers.add(current_node_id)

        else:
            spreaders.remove(current_node_id)
            graph.nodes[current_node_id]['rumor_group'] = STIFLER
            ret_graph.nodes[current_node_id]['rumor_group'] = STIFLER
            stiflers.add(current_node_id)

        spreader_lens.append(len(spreaders))
        stifler_lens.append(len(stiflers))

    assign_visual_colors(ret_graph)
    ret_graphs = [ret_graph]

    spread_node_count = nx.number_of_nodes(ret_graph)
    get_time_evolution(spreader_lens, stifler_lens, spreader_to_stifler_chance, cessation_chance, spread_node_count)

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


def convert_ignorant(current_node_id, neighbor_id, graph, spreaders, ret_graph, current_edge_id):
    neighbor_node = graph.nodes[neighbor_id]

    lambda_chance = get_ignorant_to_spreader_chance(neighbor_node)

    if random.random() <= lambda_chance:
        neighbor_node['rumor_group'] = SPREADER
        spreaders.add(neighbor_id)
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
                          export_stats=True,
                          initial_cessation_chance=0,
                          initial_spreader_to_stifler_chance=0,
                          ):
    json_graph = Gt.json_loader(graph_name)

    if isGraphCompatible(json_graph):
        sim_id = Sp.get_sim_id()
        if export_stats:
            os.mkdir(Sp.FULL_SIM_DIR + '/Sim_' + str(sim_id))

        graph = json_to_nx(json_graph)

        cessation_chance = initial_cessation_chance
        spreader_to_stifler_chance = initial_spreader_to_stifler_chance

        run_number = 1

        for i in range(run_count):
            if is_hub_start:
                start_node_id = Gt.get_largest_hub(graph)
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
                             graphs[0]
                             )

            print("run #" + str(run_number) + " of " + str(run_count))
            run_number += 1

        if export_stats:
            Sp.get_summary_stats(sim_id, 'rumor relatability', 1000, False)
    else:
        print("Graph is not compatible with the model")


def get_run_params(config_path):
    with open(config_path) as config_file:
        json_file = json.load(config_file)
        cessation_runs = round((json_file["cessation_stop"] - json_file["cessation_start"]) / 0.02) + 1
        spreader_to_stifler_runs = round(
            (json_file["spreader_to_stifler_stop"] - json_file["spreader_to_stifler_start"]) / 0.02) + 1

        return {"cessation_start": json_file["cessation_start"],
                "cessation_runs": cessation_runs,
                "spreader_to_stifler_start": json_file["spreader_to_stifler_start"],
                "spreader_to_stifler_runs": spreader_to_stifler_runs}


def run_full_rumor_spread_with_param_scaling(graph_name,
                                             run_count,
                                             is_hub_start: bool
                                             ):
    run_params = get_run_params('emailModeling/rumour_spread_limits.json')

    cessation_chance = run_params["cessation_start"]
    spreader_to_stifler_start_chance = run_params["spreader_to_stifler_start"]

    cessation_increase = 0.02
    spreader_to_stifler_increase = 0.02

    cessation_runs = run_params["cessation_runs"]
    spreader_to_stifler_runs = run_params["spreader_to_stifler_runs"]

    simulation_count = cessation_runs * spreader_to_stifler_runs
    current_simulation = 1

    for i in range(cessation_runs):
        spreader_to_stifler_chance = spreader_to_stifler_start_chance
        for j in range(spreader_to_stifler_runs):
            run_full_rumor_spread(graph_name,
                                  run_count,
                                  is_hub_start,
                                  initial_cessation_chance=cessation_chance,
                                  initial_spreader_to_stifler_chance=spreader_to_stifler_chance,
                                  )

            print("simulation " + str(current_simulation) + " of " + str(simulation_count))
            current_simulation += 1
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
                                        + strong_opponent_reactions[-2]

    average_opponent_conversion_chance = average_opponent_reactions[-1] \
                                         + average_opponent_reactions[-2]

    weak_opponent_conversion_chance = weak_opponent_reactions[-1] \
                                      + weak_opponent_reactions[-2]

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
                                  + apathetic_reactions[-2]

    there_is_something_to_it_conversion_chance = there_is_something_to_it_reactions[-1] \
                                                 + there_is_something_to_it_reactions[-2]

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
                                             + weak_covid_supporter_reactions[-2]

    weak_migration_supporter_conversion_chance = weak_migration_supporter_reactions[-1] \
                                                 + weak_migration_supporter_reactions[-2]

    strong_supporter_conversion_chance = strong_supporter_reactions[-1] \
                                         + strong_supporter_reactions[-2]

    conversion_chances = [weak_covid_supporter_conversion_chance,
                          weak_migration_supporter_conversion_chance,
                          strong_supporter_conversion_chance]

    return random.choices(conversion_chances, weights=weights)[0]


def get_time_evolution(spreader_lens, stifler_lens, spreader_to_stifler_chance, cessation_chance, node_count):
    time_evolution_stats = {
        "spreader_lens": spreader_lens,
        "stifler_lens": stifler_lens,
        "spreader_to_stifler_chance": spreader_to_stifler_chance,
        "cessation_chance": cessation_chance,
        "max_node_count": node_count
    }
    path_to_max_time_evolution = TIME_EVOLUTION_GRAPH_FOLDER \
                                 + 'd' + str(round(cessation_chance, 3)).replace('.', '') \
                                 + 'a' + str(round(spreader_to_stifler_chance, 3)).replace('.', '') \
                                 + '_max.json'

    path_to_time_evolution = TIME_EVOLUTION_GRAPH_FOLDER \
                             + 'd' + str(round(cessation_chance, 3)).replace('.', '') \
                             + 'a' + str(round(spreader_to_stifler_chance, 3)).replace('.', '') \
                             + '.json'

    if os.path.exists(path_to_time_evolution):
        path_exists = True
    else:
        path_exists = False

    if path_exists:
        with open(path_to_time_evolution, 'r', encoding='utf-8') as file:
            old_time_evolution_stats = json.load(file)
            old_spreader_lens = old_time_evolution_stats['spreader_lens']
            old_stifler_lens = old_time_evolution_stats['stifler_lens']
            old_max_node_count = old_time_evolution_stats['max_node_count']

            new_spreader_lens = spreader_lens
            new_stifler_lens = stifler_lens
            new_max_node_count = max(node_count, old_max_node_count)

            size_diff = abs(len(new_spreader_lens) - len(old_spreader_lens))

            if len(new_spreader_lens) < len(old_spreader_lens):
                new_spreader_lens.extend([new_spreader_lens[-1]] * size_diff)
            else:
                old_spreader_lens.extend([old_spreader_lens[-1]] * size_diff)

            if len(new_stifler_lens) < len(old_stifler_lens):
                new_stifler_lens.extend([new_stifler_lens[-1]] * size_diff)
            else:
                old_stifler_lens.extend([old_stifler_lens[-1]] * size_diff)

            new_spreader_lens = [x + y for x, y in zip(spreader_lens, old_spreader_lens)]
            new_stifler_lens = [x + y for x, y in zip(stifler_lens, old_stifler_lens)]

            time_evolution_stats['spreader_lens'] = new_spreader_lens
            time_evolution_stats['stifler_lens'] = new_stifler_lens
            time_evolution_stats['max_node_count'] = new_max_node_count

            if node_count > old_max_node_count:
                with open(path_to_max_time_evolution, 'w', encoding='utf-8') as max_file:
                    time_evolution_max_stats = {
                        "spreader_lens": spreader_lens,
                        "stifler_lens": stifler_lens,
                        "spreader_to_stifler_chance": spreader_to_stifler_chance,
                        "cessation_chance": cessation_chance,
                        "max_node_count": new_max_node_count
                    }

                    json.dump(time_evolution_max_stats, max_file)

    with open(path_to_time_evolution, 'w', encoding='utf-8') as file:
        json.dump(time_evolution_stats, file)
