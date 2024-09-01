#!/usr/bin/env python3

"""Contains chat related endpoints"""

import logging
from ninja import NinjaAPI
from .dependencies import JWTAuth
from utils.utils import generate_websocket_url
from .models import Conversation
from .schemas import (
    ChatSchema,
    ErrorSchema
)

logger = logging.getLogger("apps")
chat = NinjaAPI(version="1.0.0")


@chat.post(
    '/new_chat',
    auth=JWTAuth(),
    response={
        200: ChatSchema,
        400: ErrorSchema
    })
def new_chat(request):
    try:
        user = request.user
        logger.info(f"Attempting to create a new conversation for user: {user.id}")
        print(request.user)
        convo = Conversation.custom_save(user=user)
        logger.info(f"New conversation created: {convo} (ID: {convo.id})")

        if not convo:
            logger.warning("Failed to create a new conversation.")
            return 400, {"error": "Failed to create a new conversation.", "status": 400}

        websocket_url = generate_websocket_url(convo.id)
        logger.info(f"WebSocket URL generated: {websocket_url}")

        return 200, {
            "message": "Conversation successfully initiated",
            "websocket_url": websocket_url,
            "status": 200
        }

    except Exception as e:
        logger.error(f"Error in creating a new chat: {str(e)}")
        return 400, {
            "error": str(e),
            "status": 400
        }
