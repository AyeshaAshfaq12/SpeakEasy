import json
from channels.generic.websocket import AsyncWebsocketConsumer

# from googletrans import Translator, LANGUAGES

# from translate import Translator

from deep_translator import GoogleTranslator


class ChatConsumer(AsyncWebsocketConsumer):
    user_languages = {}
    room_users = {}

    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        self.language = self.scope['url_route']['kwargs']['language']

        # Add the user to the room
        if self.room_name not in ChatConsumer.room_users:
            ChatConsumer.room_users[self.room_name] = []
        ChatConsumer.room_users[self.room_name].append(self.channel_name)

        # Store user's language preference
        ChatConsumer.user_languages[self.channel_name] = self.language

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()


    async def disconnect(self, close_code):
        # Remove the user from the room
        if self.room_name in ChatConsumer.room_users and self.channel_name in ChatConsumer.room_users[self.room_name]:
            ChatConsumer.room_users[self.room_name].remove(self.channel_name)
        
        # Clean up if room becomes empty
        if not ChatConsumer.room_users[self.room_name]:
            del ChatConsumer.room_users[self.room_name]

        await self.channel_layer.group_discard(self.room_name, self.channel_name)

        if self.channel_name in ChatConsumer.user_languages:
            del ChatConsumer.user_languages[self.channel_name]


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        event = {
            'type': 'send_message',
            'message': text_data_json['message'],
            'sender': text_data_json['sender'],
        }

        await self.channel_layer.group_send(self.room_name, event)


    async def send_message(self, event):
        original_message = event['message']
        sender = event['sender']

        # Dictionary to hold translated messages for each user
        translated_messages = {}

        # Translate the message for each language in the room
        if self.room_name in ChatConsumer.room_users:
            for user_channel in ChatConsumer.room_users[self.room_name]:
                language = ChatConsumer.user_languages.get(user_channel, 'en')
                if language not in translated_messages:
                    translated_message = await self.translate_message(original_message, language)
                    translated_messages[language] = translated_message

        # Broadcast the message to all users with pre-translated messages
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'broadcast_message',
                'original_message': original_message,
                'translated_messages': translated_messages,
                'sender': sender,
            }
        )
    

    async def broadcast_message(self, event):
        # Extract the user's preferred language
        language = ChatConsumer.user_languages.get(self.channel_name, 'en')
        translated_message = event['translated_messages'].get(language, event['original_message'])

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'original_message': event['original_message'],
            'translated_message': translated_message,
            'sender': event['sender'],
        }))


    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'original_message': event['original_message'],
            'translated_message': event['translated_message'],
            'sender': event['sender'],
        }))

    
    async def translate_message(self, text, lang):
        try:
            translator = GoogleTranslator(source="auto", target=lang)
            translated_text = translator.translate(text)
            return translated_text
        except Exception as e:
            return text

    