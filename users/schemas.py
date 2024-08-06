#!/usr/bin/env python3


"""Contains user related schemas definition"""

from typing import Optional
from ninja import Schema


class UserSchema(Schema):
    """
    User schema
    """
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreateSchema(Schema):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str


class LoginSchema(Schema):
    username: str
    password: str
