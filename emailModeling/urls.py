from django.urls import path
from . import views


urlpatterns = [
    path('getGraph/', views.get_graph),
    path('getGraphList/', views.get_list_of_available_graphs),
    path('getColoring/', views.get_coloring_process),
    path('getGwTree/', views.get_gw_tree),
    path('getFullSim/', views.get_full_lnk_sim),
   ]
