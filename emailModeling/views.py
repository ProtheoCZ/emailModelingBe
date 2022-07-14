import json
from django.http import JsonResponse
# Create your views here.


def get_graph(request):
    file = open('graphData/editedGraphBigger.json')
    retjson = json.load(file)
    return JsonResponse(retjson)
