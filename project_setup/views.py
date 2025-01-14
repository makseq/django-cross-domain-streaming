import uuid
import logging

from time import sleep
from django.views import View
from django.http import JsonResponse, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from threading import Thread

from .models import ProjectSetup
from .functions import celery_run_rag_llm, run_rag_llm


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class CreateProjectSetupView(View):
    """
    POST -> creates a ProjectSetup, starts Celery task, returns { project_setup_id, request_token }
    """
    def post(self, request, *args, **kwargs):
        token = uuid.uuid4().hex
        project = ProjectSetup.objects.create(request_token=token)

        if settings.CELERY_ENABLED:
            # Launch Celery task
            celery_run_rag_llm.delay(project.id)
            logger.info(f"=> Celery task launched for project setup {project.id}")
        else:
            # Run task in a separate thread
            Thread(target=run_rag_llm, args=(project.id,)).start()
            logger.info(f"=> Thread task launched for project setup {project.id}")

        return JsonResponse({
            'project_setup_id': project.id,
            'request_token': token
        })


class SSEProjectSetupView(View):
    """
    GET -> streams partial/final results via SSE for the given project_setup_id + request_token.
    """

    def get(self, request, project_setup_id, *args, **kwargs):
        # 1. Extract the token from query or header
        token = (
            request.GET.get('request_token')
            or request.headers.get('X-Request-Token')
        )

        # 2. Validate ProjectSetup
        try:
            project = ProjectSetup.objects.get(id=project_setup_id, request_token=token)
        except ProjectSetup.DoesNotExist:
            return JsonResponse({'error': 'Invalid ID or token'}, status=403)

        # 3. Define generator for SSE
        def event_stream():
            # Tell the client: if this connection closes, do NOT try to reconnect
            yield "retry: 0\n\n"

            previous_content = None

            while True:
                # Refresh model from DB
                project.refresh_from_db()

                # If there's new content, send it
                if project.content != previous_content:
                    yield f"data: {project.content}\n\n"
                    previous_content = project.content

                # If the task is done, send a final event and stop streaming
                if project.status == 'done':
                    yield "event: complete\n"
                    yield "data: [DONE]\n\n"
                    break

                # Otherwise, wait a bit before checking again
                sleep(3)

        # 4. Build a StreamingHttpResponse to send the chunks
        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response
