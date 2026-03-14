from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Task

class TaskListView(ListView):
    model = Task
    template_name = "app/task_list.html"
    context_object_name = "tasks"

class TaskDetailView(DetailView):
    model = Task
    template_name = "app/task_detail.html"
    context_object_name = "task"

