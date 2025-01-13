from celery import shared_task
from .models import ProjectSetup
import time


@shared_task
def run_rag_llm(project_setup_id):
    # simulate a long-running process
    project = ProjectSetup.objects.get(id=project_setup_id)
    # Write partial results over time
    for i in range(5):
        time.sleep(3)  # simulate waiting for LLM
        project.content = f"Partial chunk {i+1}..."
        project.status = 'in_progress'
        project.save()

    # Final result
    project.content = "Final LLM answer here."
    project.status = 'done'
    project.save()