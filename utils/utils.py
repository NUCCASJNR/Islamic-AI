import uuid

from django.http import JsonResponse

from .hadith import get_random_hadith
from .mails import send_email


def generate_code():
    """Generates random 6digit code
    :return: The code


    """
    while True:
        uid = uuid.uuid4()
        uuid_hex = uid.hex  # convert to hex value
        otp = "".join(filter(str.isdigit, uuid_hex))[:6]
        if otp[0] != "0":  # Ensure the first digit is not 0
            return otp


def send_verification_email(user: "MainUser Instance"):
    """Handles sending a verification email.

    :param user: MainUser Instance
    :param user: MainUser Instance":
    :param user: "MainUser Instance": 
    :returns: JsonResponse: JSON response indicating success or failure.

    """
    if user is None:
        return {"status": "error", "message": "Invalid user instance provided"}
    context = {
        "first_name": user.first_name,
        "verification_code": user.verification_code,
    }

    try:
        send_email(
            subject="Welcome to IslamicAi",
            recipient_list=[user.email],
            template_name="users/verify.html",
            context=context,
        )
        return {"status": "success", "message": "Verification email sent successfully"}
    except Exception as e:
        print(str(e))
        return {"status": "error", "message": str(e)}


def send_reset_password_email(user: "MainUser Instance"):
    """Handles sending reset password mail to users

    :param user: MainUser Instance
    :param user: MainUser Instance":
    :param user: "MainUser Instance": 
    :returns: Response: JSON response indicating success or failure.

    """
    if user is None:
        return {"status": "error", "message": "Invalid user instance provided"}
    context = {"reset_token": user.reset_token}
    try:
        send_email(
            subject="Reset Password",
            recipient_list=[user.email],
            template_name="users/reset.html",
            context=context,
        )
        return {"status": "success", "message": "Reset email sent successfully"}
    except Exception as e:
        print(str(e))
        return {"status": "error", "message": str(e)}


def send_daily_hadith(user):
    """Handles sending daily hadiths to users

    :param user: 

    """
    if user is None:
        return {"status": "error", "message": "Invalid user instance provided"}
    hadith = get_random_hadith()
    context = {"arabic": hadith.get("arabic"), "english": hadith.get("english")}
    try:
        send_email(
            subject="Daily Hadith",
            recipient_list=[user.email],
            template_name="chat/hadith.html",
            context=context,
        )
        return {"status": "success", "message": "Daily hadith sent successfully"}
    except Exception as e:
        print(str(e))
        return {"status": "error", "message": str(e)}
