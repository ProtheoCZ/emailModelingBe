import json
import os
from .algorithms.GraphProcessor import GraphProcessor
from .algorithms.G_W_algorithm import full_gw_sim
from .algorithms.rumor_spread import \
    simulate_rumor_spread, run_full_rumor_spread_with_param_scaling

from .utils import StatsProvider as Sp

from django.http import JsonResponse


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_graph(request):  # POST
    file = 'graphData/' + request.body.decode('utf-8')
    ret_json = json.load(open(file))
    return JsonResponse(ret_json)


@csrf_exempt
def get_list_of_available_graphs(request):  # GET
    graph_list = [file for file in os.listdir('graphData')]
    print(graph_list)
    ret_json = {"graphList": graph_list}
    return JsonResponse(ret_json)


@csrf_exempt
def get_coloring_process(request):  # POST
    if len(request.body.decode('utf-8')) > 0:
        processor = GraphProcessor(request.body.decode('utf-8'))
        return JsonResponse(processor.process_graph_lnk())
    else:
        return JsonResponse({"graphs": [], "compatible": 1})


@csrf_exempt
def get_gw_tree(request):  # GET
    processor = GraphProcessor(None)
    return JsonResponse(processor.generate_gw_tree())


@csrf_exempt
def get_full_lnk_sim(request):
    if len(request.body.decode('utf-8')) > 0:
        processor = GraphProcessor(request.body.decode('utf-8'))
        processor.process_full_lnk()
    return JsonResponse({"graphs": [], "compatible": 1})


@csrf_exempt
def get_full_gw_sim(request):
    full_gw_sim(10)
    return JsonResponse({"graphs": [], "compatible": 1})


@csrf_exempt
def get_rumor_sim(request):
    if len(request.body.decode('utf-8')) > 0:
        return JsonResponse(simulate_rumor_spread(request.body.decode('utf-8')))
    else:
        return JsonResponse({"graphs": [], "compatible": 1})


@csrf_exempt
def get_full_rumor_sim(request):
    if len(request.body.decode('utf-8')) > 0:
        run_full_rumor_spread_with_param_scaling(request.body.decode('utf-8'), 1, False)
    return JsonResponse({"graphs": [], "compatible": 1})


@csrf_exempt
def get_summary_stats(request):
    if len(request.body.decode('utf-8')) > 0:
        Sp.get_summary_stats((request.body.decode('utf-8')), 'gw')
    return JsonResponse({"graphs": [], "compatible": 1})
