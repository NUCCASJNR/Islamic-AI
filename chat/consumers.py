
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async
from chat.models import MainUser, Conversation, Message, FAQS
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from channels.db import database_sync_to_async


logging.basicConfig(level=logging.DEBUG, filename='app.log')


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        headers = self.scope.get("headers")
        token = await self.extract_auth_token(headers)
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
        re = await self.process_stored_messages(self.chat_id)
        print(f'Saved messages: {re}')

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
                await self.handle_bot_response(message)
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
        except json.decoder.JSONDecodeError as text_data:
            logging.warning(f"Received an empty or invalid JSON message: {text_data}")
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

    @database_sync_to_async
    def get_stored_messages_sync(self, conversation_id):
        """
        Synchronously get all the stored previous messages in a conversation
        """
        try:
            messages = Message.objects.filter(conversation_id=conversation_id)
            print(messages)
            return list(messages)
        except ValueError:
            logging.info(f"These users don't have previous chats")
            return []

    async def get_stored_messages(self, conversation_id):
        """
        Asynchronously fetch stored messages by calling the sync method
        """
        messages = await self.get_stored_messages_sync(conversation_id)
        return messages

    async def process_stored_messages(self, conversation_id):
        """
        Process the stored messages and display them upon successful connection
        """
        messages = await self.get_stored_messages(conversation_id)
        for message in messages:
            obj = datetime.fromisoformat(str(message.updated_at))
            time = obj.strftime("%A, %d %B %Y, %I:%M %p")
            await self.send(text_data=json.dumps({
                "message": message.message_text,
                "response": message.response,
                "time": time
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

    async def extract_auth_token(self, headers):
        for header in headers:
            if header[0] == b'authorization':
                auth_header = header[1].decode('utf-8')
                if auth_header.startswith('Bearer '):
                    return auth_header[len('Bearer '):]
        return None

    @database_sync_to_async
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

    @database_sync_to_async
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

    @database_sync_to_async
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

    @database_sync_to_async
    def save_message_async(self, message_text, sender, user_id):
        try:
            # Fetch the conversation asynchronously
            conversation = Conversation.objects.get(
                user_id=user_id, id=self.chat_id
            )
            print(conversation)

            # Save the message using sync_to_async
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                message_text=message_text,
            )
            print(f'Saved: {message}')
            return message
        except Exception as e:
            logging.error(f"Error saving message: {e}")
            return None

    async def handle_bot_response(self, user_message):
        bot_response = await self.generate_bot_response(user_message)

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

    async def generate_bot_response(self, user_message):
        @database_sync_to_async
        def find_question(question_text):
            question = FAQS.find_obj_by(**{"question": question_text})
            return question

        @database_sync_to_async
        def update_message_response(chat_id, answer):
            Message.custom_update(
                filter_kwargs={'conversation': chat_id},
                update_kwargs={'response': answer}
            )

        question = await find_question(user_message)
        if question:
            chat_id = self.chat_id
            await update_message_response(chat_id, question.answer)
            return question.answer
        else:
            return "Heyyy"
