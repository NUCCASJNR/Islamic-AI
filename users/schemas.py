#!/usr/bin/env python3
"""Contains user related schemas definition"""
from typing import Optional

from ninja import Schema


class UserSchema(Schema):
    """ """

    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreateSchema(Schema):
    """ """

    username: str
    password: str
    email: str
    first_name: str
    last_name: str


class LoginSchema(Schema):
    """ """

    username: str
    password: str


class ErrorSchema(Schema):
    """ """
    error: str


class MessageSchema(Schema):
    """Message schema"""
    message: str


class EmailVerificationSchema(Schema):
    """
    Schema for verifying user verification code
    """
    verification_code: int
