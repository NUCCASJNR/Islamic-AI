#!/usr/bin/env python3
"""Contains user related API endpoints"""
import logging
from typing import Optional

from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from rest_framework_simplejwt.tokens import RefreshToken

from .models import MainUser
from .schemas import (
    MessageSchema,
    UserCreateSchema,
    ErrorSchema,
    EmailVerificationSchema,
    LoginSchema,
    LoginResponseSchema,
    ResetPasswordSchema,
    ChangePasswordSchema,
)
from utils.utils import generate_code
from utils.utils import send_reset_password_email, send_verification_email

logger = logging.getLogger("apps")
api = NinjaAPI()


@api.get("/", response={200: MessageSchema})
def home(request):
    return 200, {
        "message": "Welcome here, doc here: https://documenter.getpostman.com/view/28289943/2sA3rzLYfH",
        "status": 200,
    }


@api.post("/auth/signup", response={201: MessageSchema, 400: ErrorSchema})
def signup(request, payload: UserCreateSchema):
    """View for registering a new user

    :param request: Request object
    :param payload: User payload
    :param payload: UserCreateSchema:
    :returns: 201 or 400

    """
    email: str = payload.email
    username: str = payload.username
    if MainUser.custom_get(email=email):
        return 400, {"error": "Email already exists", "status": 400}
    if MainUser.custom_get(username=username):
        return 400, {"error": "Username already exists", "status": 400}
    otp: int = generate_code()
    key = f"Verification_code:{otp}"
    payload_data = payload.dict()
    payload_data["verification_code"] = otp
    user = MainUser.custom_save(**payload_data)
    logger.debug(f"Setting cache with key: {key}, otp: {otp}")
    response = cache.set(key, otp, 60 * 30)
    # Debugging: check if key can be retrieved from cache
    cached_otp = cache.get(key)
    logger.debug(f"Cached OTP: {cached_otp}")
    if cached_otp != otp:
        logger.error("Error: OTP not properly set in cache.")
    send_verification_email(user)
    # Serialize the user object using UserResponseSchema

    return 201, {
        "message": "Registration successful," " Check your email for verification code",
        "status": 201,
    }


@api.post("/email-verification", response={200: MessageSchema, 400: ErrorSchema})
def email_verification(request, payload: EmailVerificationSchema):
    """
    API route for verifying user's email address
    :param request: Request Obj
    :param payload: Email verification SCHEMA
    :return: 200 if successful else 400
    """
    otp = payload.verification_code
    key = f"Verification_code:{otp}"
    if cache.get(key):
        user = MainUser.custom_get(verification_code=otp)
        user.is_verified = True
        user.verification_code = None
        user.save()
        cache.delete(key)
        return 200, {"message": "Email verification successful", "status": 200}
    return 400, {"error": "Invalid verification code", "status": 400}


@api.post("/auth/login", response={200: LoginResponseSchema, 400: ErrorSchema})
def user_login(request, payload: LoginSchema):
    """
    API view for logging in user
    :param request: Request object
    :param payload: LoginSchema
    :return: 200 if successful else 400
    """
    user = None
    email = payload.email
    password = payload.password
    username = payload.username
    if email:
        user = email
    else:
        user = username
    print(user)
    auth_user = authenticate(request, username=user, password=password)
    print(auth_user)
    if auth_user is not None:
        if not auth_user.is_verified:
            return 400, {
                "error": "You need to verify your account to login",
                "status": 400,
            }
        login(request, auth_user)
        refresh = RefreshToken.for_user(auth_user)
        return 200, {
            "message": "Login Successful!",
            "access_token": str(refresh.access_token),
            "status": 200,
        }
    return 400, {"error": "Invalid username or password", "status": 400}


@api.post("/reset-password", response={200: MessageSchema, 400: ErrorSchema})
def reset_password(request, payload: ResetPasswordSchema):
    """
    API route for resetting user password
    :param request: Request obj
    :param payload: ResetPasswordSchema
    :return: 200 if successful else 400
    """
    print(payload)
    email = payload.email
    user = MainUser.custom_get(email=email)
    if user:
        reset_token = generate_code()
        key = f"Reset_token:{reset_token}"
        user.reset_token = reset_token
        user.save()
        cache.set(key, reset_token, 60 * 30)
        send_reset_password_email(user)
        return 200, {"message": "Reset token successfully sent!", "status": 200}
    return 400, {"error": "Invalid email address", "status": 400}


@api.post("/change-password", response={200: MessageSchema, 400: ErrorSchema})
def change_password(request, payload: ChangePasswordSchema):
    """
    API route for updating user password
    :param request: Request obj
    :param payload: ChangePasswordSchema
    :return: 200 if successful else 400
    """
    reset_token = payload.reset_token
    password = payload.password
    key = f"Reset_token:{reset_token}"
    if cache.get(key):
        MainUser.custom_update(
            filter_kwargs={"reset_token": reset_token},
            update_kwargs={"password": password, "reset_token": None},
        )
        cache.delete(key)
        return 200, {"message": "Password has been successfully updated", "status": 200}
    return 400, {"error": "Invalid Reset token", "status": 400}
