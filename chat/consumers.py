import json
import logging
from datetime import datetime

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import AccessToken

from chat.models import Conversation
from chat.models import MainUser
from chat.models import Message

logging.basicConfig(level=logging.DEBUG, filename="app.log")


class MessageConsumer(AsyncWebsocketConsumer):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.user = None
        self.user_id = None
        self.sender_id = None

    async def connect(self):
        """
        Connect method
        :return: Nothing
        """
        self.sender_id = self.scope["url_route"]["kwargs"]["user_id"]
        token = self.scope.get("query_string").decode().split("Bearer%20")[1]
        auth_info = await self.get_auth_info(token)

        if not auth_info["status"]:
            await self.close()
            return f'Error: {auth_info["response"]}'

        self.user_id = auth_info.get("user_id", None)
        self.user = await self.get_user_by_id(auth_info["user_id"])

        if not self.user:
            await self.close()
            return "Error: User not found"

        # Create or get the conversation
        conversation = await self.get_or_create_conversation(self.user_id)
        self.room_group_name = f"chat_{conversation.id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    def get_conversation(self, room):
        """

        :param room:

        """
        return str(room.split("_")[1])

    async def disconnect(self, close_code):
        """
        Disconnect method
        :param close_code: Close code
        :return:
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receives incoming messages
        :param text_data: Incoming message
        :return: Processed messages
        """
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            sender = text_data_json.get("sender", self.user.username)

            # Save the message
            response = await self.save_message_async(message, sender, self.user_id)
            if response is not None:
                obj = datetime.fromisoformat(str(response.updated_at))
                time = obj.strftime("%A, %d %B %Y, %I:%M %p")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat.message",
                        "message": message,
                        "sender": sender,
                        "time": time,
                    },
                )
            else:
                logging.error("Failed to save message")
        except json.decoder.JSONDecodeError:
            logging.warning("Received an empty or invalid JSON message")
        except Exception as e:
            logging.error(f"Error processing received message: {e}")

    async def chat_message(self, event):
        """
        Chat message
        :param event:
        :return:
        """
        message = event["message"]
        sender = event["sender"]
        logging.info(
            "Sending message '%s' from sender '%s' to room '%s'",
            message,
            sender,
            self.room_group_name,
        )
        await self.send(
            text_data=json.dumps(
                {"message": message, "sender": sender, "time": event["time"]}
            )
        )

    async def get_auth_info(self, token):
        """
        Get authentication info from a JWT token
        :param token: JWT token
        :return: User ID or False
        """
        try:
            decoded_token = AccessToken(token)
            if decoded_token.get("user_id"):
                return {"status": True, "user_id": decoded_token.get("user_id")}
            return False
        except Exception as e:
            return {"status": False, "response": str(e)}

    async def close(self):
        pass

    @sync_to_async
    def get_user_by_id(self, user_id):
        """Retrieve a user object by ID

        :param user_id: User ID
        :returns: User object or None

        """
        try:
            user = MainUser.objects.get(id=user_id)
            return user
        except MainUser.DoesNotExist:
            return None
        except Exception as e:
            return f"Error: {e}"

    @sync_to_async
    def get_or_create_conversation(self, user_id):
        """Get or create a conversation for the user

        :param user_id: User ID
        :returns: Conversation object

        """
        try:
            conversation, created = Conversation.objects.get_or_create(
                user_id=user_id, status="active", defaults={"context_data": {}}
            )
            return conversation
        except Exception as e:
            logging.error(f"Error creating conversation: {e}")
            return None

    @sync_to_async
    def save_message_async(self, message_text, sender, user_id):
        """Save a message to the conversation

        :param message_text: Text of the message
        :param sender: Sender's ID or name
        :param user_id: User ID
        :returns: Message object or None

        """
        try:
            conversation = Conversation.objects.get(user_id=user_id, status="active")
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                message_text=message_text,
                response_type="text",
            )
            return message
        except Conversation.DoesNotExist:
            logging.error("No active conversation found")
            return None
        except Exception as e:
            logging.error(f"Error saving message: {e}")
            return None
