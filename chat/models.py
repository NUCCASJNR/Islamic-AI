#!/usr/bin/env python3

"""Contains chat related models"""

from utils.base_model import BaseModel, models
from users.models import MainUser

CONVERSATION_CHOICES = [
    ('active', 'Active'),
    ('completed', 'Completed'),
    ('escalated', 'Escalated')
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
