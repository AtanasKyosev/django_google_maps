from django.shortcuts import render
from django.views.generic import ListView

from project_content.models import Locations


class HomeView(ListView):
    template_name = "project_content/home.html"
    context_object_name = 'mydata'
    model = Locations
    success_url = "/"
