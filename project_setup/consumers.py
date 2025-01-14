# core/consumers.py
import json
from time import sleep
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ProjectSetup


class ProjectSetupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the socket, but not authenticated yet
        await self.accept()
        self.authenticated = False
        self.project_setup = None

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "auth_init":
            token = data.get("token")
            if await self.validate_token(token):
                self.authenticated = True
                # Start streaming partial updates
                await self.stream_updates()
            else:
                # If invalid token, close
                await self.close()
        else:
            # If user hasn't authenticated yet, close or ignore
            if not self.authenticated:
                await self.close()
            else:
                # Handle other messages
                pass

    async def disconnect(self, code):
        print(f"WebSocket disconnected with code {code}")

    @sync_to_async
    def validate_token(self, token):
        try:
            ps = ProjectSetup.objects.get(request_token=token)
            self.project_setup = ps  # store so we know which record to poll
            return True
        except ProjectSetup.DoesNotExist:
            return False

    async def stream_updates(self):
        prev_content = None

        while True:
            data = await self.get_project_data()
            if not data:
                # The record was deleted or something
                await self.close()
                break

            if data["content"] != prev_content:
                await self.send(json.dumps({
                    "content": data["content"],
                    "status": data["status"]
                }))
                prev_content = data["content"]

            if data["status"] == "done":
                await self.close()
                break

            await self.sleep_async(3)

    @sync_to_async
    def get_project_data(self):
        # re-query the stored project_setup
        if not self.project_setup:
            return None
        self.project_setup.refresh_from_db()
        return {
            "content": self.project_setup.content,
            "status": self.project_setup.status
        }

    @sync_to_async
    def sleep_async(self, secs):
        sleep(secs)