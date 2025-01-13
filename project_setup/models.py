from django.db import models

class ProjectSetup(models.Model):
    request_token = models.CharField(max_length=100, unique=True)
    content = models.TextField(blank=True, null=True)  # store the LLM output or partial text
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
