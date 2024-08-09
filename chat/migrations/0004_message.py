# Generated by Django 4.2.11 on 2024-08-09 05:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """ """

    dependencies = [
        ("chat", "0003_remove_conversation_end_time_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sender",
                    models.CharField(
                        choices=[("user", "User"), ("bot", "Bot")], max_length=10
                    ),
                ),
                ("message_text", models.TextField()),
                (
                    "response_type",
                    models.CharField(
                        choices=[
                            ("text", "Text"),
                            ("suggestion", "Suggestion"),
                            ("follow-up", "Follow-up"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="chat.conversation",
                    ),
                ),
            ],
        ),
    ]
