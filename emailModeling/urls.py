from django.urls import path
from . import views


urlpatterns = [
    path('getGraph/', views.get_graph),
    path('getGraphList/', views.get_list_of_available_graphs)
   ]
