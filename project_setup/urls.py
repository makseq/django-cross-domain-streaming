from django.urls import path
from .views import CreateProjectSetupView, SSEProjectSetupView


urlpatterns = [
    path('api/project-setup/create/', CreateProjectSetupView.as_view(), name='create_project_setup'),
    path('api/project-setup/<int:project_setup_id>/sse/', SSEProjectSetupView.as_view(), name='sse_project_setup'),
]
