#!/usr/bin/env python3
"""Contains user related schemas definition"""
from typing import Optional

from ninja import Schema
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import model_validator
from pydantic import root_validator


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
    """ """
    email: Optional[EmailStr] = None
    password: str

    @model_validator(mode="before")
    def check_email_or_username(cls, values):
        """

        :param values: 

        """
        email, username = values.get("email"), values.get("username")
        if not email and not username:
            raise ValueError("Either email or username must be provided")
        return values


class ErrorSchema(Schema):
    """ """

    error: str
    status: int


class MessageSchema(Schema):
    """Message schema"""

    message: str
    status: int


class EmailVerificationSchema(Schema):
    """Schema for verifying user verification code"""

    verification_code: int


class LoginResponseSchema(Schema):
    """Login Response Schema"""

    message: str
    status: int
    access_token: str


class ResetPasswordSchema(Schema):
    """Schema for resetting user password"""

    email: str


class ChangePasswordSchema(Schema):
    """Schema for updating user password"""

    password: str
    reset_token: int
