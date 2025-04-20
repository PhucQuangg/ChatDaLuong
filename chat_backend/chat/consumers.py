import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message, WebSocketSession, ChatUser, AIResponse
from .AI_Service import CohereService
from asgiref.sync import sync_to_async
import logging
from django.contrib.auth.models import AnonymousUser


logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        if self.user.is_admin:
            conversations = await self.get_all_conversations_of_admin()
            self.room_group_names = [f"conversation_{conv.id}" for conv in conversations]
            for room in self.room_group_names:
                await self.channel_layer.group_add(room, self.channel_name)
                

            await self.channel_layer.group_add("admin_notifications", self.channel_name)
            await self.send_online_users()  # Gửi danh sách user online khi admin kết nối

        else:
            conversation, created = await self.get_or_create_conversation()
            if conversation:
                self.room_group_name = f"conversation_{conversation.id}"
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)

                if created:
                    await self.channel_layer.group_send(
                        "admin_notifications",
                        {
                            "type": "new_conversation",
                            "conversation_id": conversation.id
                        }
                    )

        await self.save_websocket_session()
        await self.send_online_users()  # Gửi danh sách user online khi user kết nối
        await self.accept()
        


    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await self.remove_websocket_session()
        await self.send_online_users()

        if not isinstance(self.user, AnonymousUser) and getattr(self.user, "is_admin", False):
            await self.channel_layer.group_discard("admin_notifications", self.channel_name)


    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data["content"]

        if not self.user.is_authenticated:
            return

        sender = self.user
        conversation_id = data.get("conversation_id")
        if conversation_id:
            conversation = await self.get_conversation_by_id(conversation_id)
        else:
            conversation = await self.get_latest_conversation_of_user(sender)
            if not conversation:
                conversation, _ = await self.get_or_create_conversation()

        role = "admin" if self.user.is_admin else "user"

        if conversation:
            group_name = f"conversation_{conversation.id}"
            await self.save_message(conversation, content)

            admin_session = await self.get_admin_session()

            if not admin_session:
                ai_reply = await CohereService.get_ai_reply(content)
                await self.save_ai_response(conversation, content, ai_reply)

                await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": "chat_message",
                        "sender": "AI",
                        "content": ai_reply,
                        "conversation_id": conversation.id,
                        "role": "AI"
                    }
                )
            else:
                await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": "chat_message",
                        "sender": sender.username,
                        "content": content,
                        "conversation_id": conversation.id,
                        "role": role
                    }
                )
    async def new_conversation(self, event):
        conversation_id = event["conversation_id"]
        room_group_name = f"conversation_{conversation_id}"
        conversation = await sync_to_async(Conversation.objects.get, thread_sensitive=True)(id=event["conversation_id"])
        username = await sync_to_async(lambda: conversation.user.username, thread_sensitive=True)()

        await self.channel_layer.group_add(room_group_name, self.channel_name)

        await self.send(text_data=json.dumps({
            "type": "new_conversation",
            "conversation_id": conversation_id,
            "username": username
        }))

    async def chat_message(self, event):
        conversation = await sync_to_async(Conversation.objects.get, thread_sensitive=True)(id=event["conversation_id"])
        username = await sync_to_async(lambda: conversation.user.username, thread_sensitive=True)()
        await self.send(text_data=json.dumps({
            "sender": event["sender"],
            "content": event["content"],
            "conversation_id": event["conversation_id"],
            "role": event["role"],
            "username": username
        }))

    async def send_online_users(self):
        online_users = await self.get_online_users()

        await self.channel_layer.group_send(
            "admin_notifications",
            {
                "type": "online_users",
                "online_users": [{"id": user.id, "username": user.username} for user in online_users]
            }
        )

    async def online_users(self, event):
        await self.send(text_data=json.dumps({
            "type": "online_users",
            "users": event["online_users"]
        }))

    @database_sync_to_async
    def get_online_users(self):
        sessions = WebSocketSession.objects.select_related("user").all()
        return [session.user for session in sessions if not session.user.is_admin]  

    @database_sync_to_async
    def get_conversation_by_id(self, conversation_id):
        return Conversation.objects.filter(id=conversation_id).first()

    @database_sync_to_async
    def get_all_conversations_of_admin(self):
        if not self.user.is_admin:
            return []
        return list(Conversation.objects.filter(admin=self.user))

    @database_sync_to_async
    def get_or_create_conversation(self):
        if self.user.is_admin:
            return None, False
        admin_user = ChatUser.objects.filter(is_admin=True).first()
        if not admin_user:
            return None, False
        conversation, created = Conversation.objects.get_or_create(user=self.user, admin=admin_user)
        if created:
            conversation.name = f"chat_{conversation.id}"
            conversation.save()
        return conversation, created

    @database_sync_to_async
    def get_latest_conversation_of_user(self, sender):
        if sender.is_admin:
            last_message = Message.objects.filter(conversation__admin=sender).order_by("-created_at").first()
            return last_message.conversation if last_message else None
        return Conversation.objects.filter(user=sender).order_by("-created_at").first()

    @database_sync_to_async
    def save_message(self, conversation, content):
        return Message.objects.create(conversation=conversation, sender=self.user, text=content)

    @database_sync_to_async
    def save_websocket_session(self):
        WebSocketSession.objects.update_or_create(
            user=self.user,
            session_id=self.channel_name,
            defaults={"last_active": None}
        )

    @database_sync_to_async
    def remove_websocket_session(self):
        WebSocketSession.objects.filter(session_id=self.channel_name).delete()

    @database_sync_to_async
    def get_admin_session(self):
        return WebSocketSession.objects.filter(user__is_admin=True).first()

    @database_sync_to_async
    def save_ai_response(self, conversation, content, ai_reply):
        return AIResponse.objects.create(
            conversation=conversation,
            message_text=content,
            ai_reply=ai_reply
        )