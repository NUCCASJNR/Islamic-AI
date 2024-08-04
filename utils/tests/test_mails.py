import pytest
from django.core import mail

from utils.mails import send_email


@pytest.mark.django_db
def test_send_email(mocker):
    """

    :param mocker:

    """
    # Arrange
    subject = "Test Subject"
    recipient_list = ["recipient@example.com"]
    template_name = "users/verify.html"
    context = {"username": "John Doe", "verification_code": 123456}

    # Mock the template rendering to return a full HTML content
    mocker.patch(
        "django.template.loader.render_to_string",
        return_value="<p>Welcome to Sabirent</p><p>Your verification"
        " code is: <strong>123456</strong></p>",
    )

    # Act
    send_email(subject, recipient_list, template_name, context)

    # Assert
    assert len(mail.outbox) == 1  # Check that one email was sent
    email = mail.outbox[0]
    print(f"Email Subject: {email.subject}")
    print(f"Email Recipients: {email.to}")
    print(f"Plain Text Content:\n{email.body}")
    print(f"HTML Content:\n{email.alternatives[0][0]}")

    assert email.subject == subject
    assert email.to == recipient_list
    assert "Welcome to Sabirent" in email.body
    assert "Your verification code is: 123456" in email.body
    assert len(email.alternatives) == 1
    assert email.alternatives[0][1] == "text/html"
    assert "Welcome to Sabirent" in email.alternatives[0][0]
    assert ("Your verification code is: <strong>123456</strong>"
            in email.alternatives[0][0])
