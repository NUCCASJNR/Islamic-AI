import pytest
from django.http import JsonResponse

from users.models import MainUser
from utils.utils import send_verification_email


@pytest.fixture
def user_instance(db):
    """

    :param db:

    """
    # Create and return a MainUser instance for testing

    return MainUser.objects.create(
        username="testuser", email="test@example.com", verification_code="123456"
    )


@pytest.mark.django_db
def test_send_welcome_email(mocker, user_instance):
    """
    Test for sending a welcome email
    :param mocker:
    :param user_instance:
    """
    # Mock the send_email function
    send_email_mock = mocker.patch("utils.utils.send_email")

    # Case 1: Successful email sending
    response = send_verification_email(user_instance)

    # Assert that send_email was called with the correct parameters
    send_email_mock.assert_called_once_with(
        subject="Welcome to IslamicAi",
        recipient_list=[user_instance.email],
        template_name="users/verify.html",
        context={
            "first_name": user_instance.first_name,
            "verification_code": user_instance.verification_code,
        },
    )

    assert response.get("status") == "success"
    assert response.get("message") == "Verification email sent successfully"

    # Case 2: Email sending failure (mocking an exception)
    send_email_mock.reset_mock()  # Reset mock to track calls for the new case
    send_email_mock.side_effect = Exception("Email sending failed")

    response = send_verification_email(user_instance)

    # Assert that send_email was called with the correct parameters
    send_email_mock.assert_called_once_with(
        subject="Welcome to IslamicAi",
        recipient_list=[user_instance.email],
        template_name="users/verify.html",
        context={
            "first_name": user_instance.first_name,
            "verification_code": user_instance.verification_code,
        },
    )

    assert response.get("status") == "error"

    # Case 3: Invalid user instance (e.g., None)
    send_email_mock.reset_mock()  # Reset mock to track calls for the new case

    response = send_verification_email(None)  # Passing None as user instance

    # Assert that send_email was not called
    send_email_mock.assert_not_called()
    assert response == {"status": "error", "message": "Invalid user instance provided"}
    assert response.get("status") == "error"
    # Add more test cases as needed for different edge cases
