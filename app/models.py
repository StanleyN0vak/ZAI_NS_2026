from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "project"
        verbose_name_plural = "projekty"

    def __str__(self) -> str:
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "tag"
        verbose_name_plural = "tag"

    def __str__(self) -> str:
        return self.name
    
class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To do"
        DOING = "doing", "Doing"
        DONE = "done", "Done"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="app",
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.TODO,
    )

    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="app",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "zadania"
        verbose_name_plural = "zadania"

    def __str__(self) -> str:
        return self.title
