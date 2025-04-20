from django.db import models
from django.contrib.auth.models import AbstractUser

class ChatUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    def __str__(self):
        return self.username
    

class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE, related_name="user_conversations", null=True, blank=True)
    admin = models.ForeignKey(ChatUser, on_delete=models.CASCADE, related_name="admin_conversations", null=True, blank=True)  # Thêm null=True, blank=True

    def __str__(self):
        return f'Conversation {self.id}'



class Message(models.Model):
    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(ChatUser, null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username if self.sender else 'System'}: {self.text[:20]}"


class WebSocketSession(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE, related_name="sessions")
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Session {self.session_id} for {self.user.username}"


class AIResponse(models.Model):
    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="ai_responses", null=True, blank=True)  # Thêm null=True, blank=True
    message_text = models.TextField(default="")
    ai_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Reply in Conversation {self.conversation.id if self.conversation else 'No Conversation'}"


