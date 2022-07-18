import json
import os

from django.http import JsonResponse, HttpResponse


# Create your views here.


def get_graph(request):
    file = open('graphData/editedGraphBigger.json')
    ret_json = json.load(file)
    return JsonResponse(ret_json)


def get_list_of_available_graphs(request):
    # graph_list = os.listdir('graphData')
    graph_list = [file for file in os.listdir('graphData')]
    print(graph_list)
    ret_json = {"graphList": graph_list}
    return JsonResponse(ret_json)
