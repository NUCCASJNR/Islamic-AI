#!/usr/bin/env python3
"""Contains user related schemas definition"""
from typing import Optional
from ninja import Schema
from pydantic import BaseModel, EmailStr, root_validator


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


class LoginSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str

    @model_validator(mode='before')
    def check_email_or_username(cls, values):
        email, username = values.get('email'), values.get('username')
        if not email and not username:
            raise ValueError('Either email or username must be provided')
        return values


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
