
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async
from chat.models import MainUser, Conversation, Message
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from channels.db import database_sync_to_async


logging.basicConfig(level=logging.DEBUG, filename='app.log')


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        print(f"Chat ID: {self.chat_id}")
        token = self.scope.get("query_string").decode().split("Bearer%20")[1]
        print(f"Token: {token}")

        auth_info = await self.get_auth_info(token)
        print(f"Auth Info: {auth_info}")

        if not auth_info['status']:
            await self.close()
            print(f"Authentication failed: {auth_info['response']}")
            return

        self.user_id = auth_info.get('user_id', None)
        self.user = await self.get_user_by_id(auth_info['user_id'])
        print(f"User: {self.user}")
        if not self.user:
            await self.close()
            print("User not found")
            return

        owner = await self.confirm_convo_owner(self.user_id, self.chat_id)
        print(f'res: {owner}')
        if not owner:
            await self.close()
            print('You cant Access this conversation')
            return
        self.room_group_name = f"chat_{self.chat_id}"
        print(f"Room Group Name: {self.room_group_name}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    def get_conversation(self, room):
        return str(room.split("_")[1])

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        else:
            print('Group name not set')

    async def receive(self, text_data):
        """
        Receives incoming messages
        :param text_data: Incoming message
        :return: Processed messages
        """
        try:
            print(f'Json: {text_data}')
            text_data_json = json.loads(text_data)
            print(f'Json data: {text_data_json}')
            message = text_data_json["message"]
            sender = text_data_json.get("sender", self.user.username)
            print(f'id: {self.chat_id}')

            # Save the message
            response = await self.save_message_async(message, "sender", self.user_id)
            print(f'response: {response}')
            if response is not None:
                obj = datetime.fromisoformat(str(response.updated_at))
                time = obj.strftime("%A, %d %B %Y, %I:%M %p")
                await self.channel_layer.group_send(
                    self.room_group_name, {
                        "type": "chat.message",
                        "message": message,
                        "sender": sender,
                        "time": time
                    }
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
        print(f'sender: {sender} message{message}')
        logging.info("Sending message '%s' from sender '%s' to room '%s'", message, sender, self.room_group_name)
        await self.send(text_data=json.dumps({
            "message": message,
            "sender": sender,
            "time": event["time"]
        }))

    async def get_auth_info(self, token):
        """
        Get authentication info from a JWT token
        :param token: JWT token
        :return: User ID or False
        """
        try:
            decoded_token = AccessToken(token)
            if decoded_token.get("user_id"):
                return {
                    "status": True,
                    "user_id": decoded_token.get("user_id")
                }
            return False
        except Exception as e:
            return {
                "status": False,
                "response": str(e)
            }

    @sync_to_async
    def confirm_convo_owner(self, user_id, convo_id):
        """
        Confirms if a user owns a conversation before granting access
        """
        convo = Conversation.custom_get(**{'id': convo_id})
        if convo:
            if str(convo.user.id) == user_id:
                return True
            else:
                return False
        return False

    async def close(self):
        pass

    @sync_to_async
    def get_user_by_id(self, user_id):
        """
        Retrieve a user object by ID
        :param user_id: User ID
        :return: User object or None
        """
        try:
            user = MainUser.objects.get(id=user_id)
            return user
        except MainUser.DoesNotExist:
            return None
        except Exception as e:
            return f'Error: {e}'

    @sync_to_async
    def get_or_create_conversation(self, user_id):
        """
        Get or create a conversation for the user
        :param user_id: User ID
        :return: Conversation object
        """
        try:
            conversation, created = Conversation.objects.get_or_create(
                user_id=user_id,
                status="active",
                defaults={'context_data': {}}
            )
            return conversation
        except Exception as e:
            logging.error(f"Error creating conversation: {e}")
            return None

    @sync_to_async
    def save_message_async(self, message_text, sender, user_id):
        """
        Save a message to the conversation
        :param message_text: Text of the message
        :param sender: Sender's ID or name
        :param user_id: User ID
        :return: Message object or None
        """
        try:
            conversation = Conversation.custom_get(**{"user_id": user_id, "id": self.chat_id})
            print(conversation)
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                message_text=message_text,
            )
            return message
        except Conversation.DoesNotExist:
            logging.error("No active conversation found")
            return None
        except Exception as e:
            logging.error(f"Error saving message: {e}")
            return None

    async def handle_bot_response(self, user_message):
        bot_response = self.generate_bot_response(user_message)

        # Send the bot's response to the WebSocket channel
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": bot_response,
                "sender": "bot",
                "time": datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
            }
        )

    def generate_bot_response(self, user_message):
        return "This is a bot's response to your message."
