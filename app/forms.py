from django.forms import DateTimeField, ModelForm
from django.core.exceptions import ValidationError
from .models import Task, Project

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "project",
            "due_date",
            "tags"
            ]
        
class ProjectForm(ModelForm):
    created_at = DateTimeField(disabled=True, required=False)
    class Meta:
        model = Project
        fields = ["name", "description"]