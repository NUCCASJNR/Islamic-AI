#!/usr/bin/env python3

"""Contains chat related models"""

from utils.base_model import BaseModel, models
from users.models import MainUser

CONVERSATION_CHOICES = [
    ('active', 'Active'),
    ('completed', 'Completed'),
    ('escalated', 'Escalated')
]

MESSAGE_CHOICES = [
    ('text', 'Text'),
    ('suggestion', 'Suggestion'),
    ('follow-up', 'Follow-up')
]

SENDER_CHOICES = [
    ('user', 'User'),
    ('bot', 'Bot')
]


class Conversation(BaseModel):
    """Conversation Model"""
    user = models.ForeignKey(MainUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=50,
                              choices=CONVERSATION_CHOICES)
    context_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "conversations"

    def __str__(self):
        return f"Conversation {self.id} with {self.user.username}"


class Message(models.Model):
    """Message Model"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message_text = models.TextField()
    response_type = models.CharField(max_length=50, choices=MESSAGE_CHOICES)

    class Meta:
        db_table = "messages"

    def __str__(self):
        return f"Message {self.id} from {self.sender} in {self.conversation.id}"
