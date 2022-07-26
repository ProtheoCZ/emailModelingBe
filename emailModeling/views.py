import json
import os
from .algorithms.GraphProcessor import GraphProcessor

from django.http import JsonResponse, HttpResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_graph(request):  # POST
    # file = open('graphData/editedGraphBigger.json')
    file = 'graphData/' + request.body.decode('utf-8')
    # file = open('graphData/' + request.body.decode('utf-8'))
    ret_json = json.load(open(file))
    return JsonResponse(ret_json)


@csrf_exempt
def get_list_of_available_graphs(request):  # GET
    # graph_list = os.listdir('graphData')
    graph_list = [file for file in os.listdir('graphData')]
    print(graph_list)
    ret_json = {"graphList": graph_list}
    return JsonResponse(ret_json)


@csrf_exempt
def get_coloring_process(request):  # POST
    if len(request.body.decode('utf-8')) > 0:
        processor = GraphProcessor(request.body.decode('utf-8'))
        return JsonResponse(processor.process_graph())
    else:
        return JsonResponse({"graphs": []})

