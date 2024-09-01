#!/usr/bin/env python3

"""Contains chat related scehams information"""

from ninja import Schema
from pydantic import BaseModel


class ErrorSchema(Schema):
    error: str
    status: int


class ChatSchema(Schema):
    message: str
    status: int
    websocket_url: str
