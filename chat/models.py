#!/usr/bin/env python3
"""Contains chat related models"""
from users.models import MainUser
from utils.base_model import BaseModel
from utils.base_model import models

CONVERSATION_CHOICES = [
    ("active", "Active"),
    ("completed", "Completed"),
    ("escalated", "Escalated"),
]


class Conversation(BaseModel):
    """Conversation Model"""

    user = models.ForeignKey(MainUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=CONVERSATION_CHOICES)
    context_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Conversation {self.id} with {self.user.username}"
