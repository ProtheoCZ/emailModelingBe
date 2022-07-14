from django.urls import path
from . import views


urlpatterns = [
    path('getGraph/', views.get_graph)
   ]
