#!/usr/bin/env python3

"""Contains user related API endpoints"""

from typing import Optional
from ninja import NinjaAPI, Schema
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import MainUser
from .schemas import UserCreateSchema, UserResponseSchema, MessageSchema
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja.responses import Response
from utils.utils import (
    generate_code,
    send_verification_email,
    send_reset_password_email,
)
from django.core.cache import cache
from django.contrib.auth import authenticate, login
import logging

logger = logging.getLogger("apps")
api = NinjaAPI()


@api.post("/auth/signup", response={201: UserResponseSchema, 400: MessageSchema})
def signup(request, payload: UserCreateSchema):
    """
    View for registering a new user
    :param request: Request object
    :param payload: User payload
    :return: 201 or 400
    """
    email: str = payload.email
    username: str = payload.username
    if MainUser.custom_get(email=email):
        return JsonResponse({"message": "User already exists"}, status=400)
    if MainUser.custom_get(username=username):
        return JsonResponse({"message": "Username already exists"}, status=400)
    otp: int = generate_code()
    key = f"Verification_code:{otp}"
    payload_data = payload.dict()
    payload_data["verification_code"] = otp
    user = MainUser.custom_save(**payload_data)
    logger.debug(f"Setting cache with key: {key}, otp: {otp}")
    response = cache.set(key, otp, 60 * 10)
    # Debugging: check if key can be retrieved from cache
    cached_otp = cache.get(key)
    logger.debug(f"Cached OTP: {cached_otp}")
    if cached_otp != otp:
        logger.error("Error: OTP not properly set in cache.")
    send_verification_email(user)
    # Serialize the user object using UserResponseSchema

    return JsonResponse({"message": "User registered successfully", "status": 201})
