import pytest
from django.core import mail
from utils.utils import send_email


@pytest.mark.django_db
def test_send_email(mocker):
    """
    Test for sending an email
    :param mocker:
    """
    # Arrange
    subject = "Test Subject"
    recipient_list = ["recipient@example.com"]
    template_name = "users/verify.html"
    context = {"first_name": "John Doe", "verification_code": 123456}

    # Mock the template rendering to return a full HTML content
    mocker.patch(
        "django.template.loader.render_to_string",
        return_value="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to IslamicAI</title>
            <style>
                body {
                    font-family: 'Amiri', serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }
                .container {
                    max-width: 600px;
                    margin: 30px auto;
                    background: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border: 1px solid #d4af37;
                }
                h1 {
                    color: #007BFF;
                    text-align: center;
                    border-bottom: 2px solid #d4af37;
                    padding-bottom: 10px;
                }
                p {
                    margin: 10px 0;
                }
                .highlight {
                    font-weight: bold;
                    color: #007BFF;
                }
                .arabic-pattern {
                    background-image: url('https://www.transparenttextures.com/patterns/arabic-pattern.png');
                    background-size: cover;
                    border-radius: 8px 8px 0 0;
                    padding: 20px;
                    text-align: center;
                    color: #fff;
                }
                .arabic-text {
                    font-family: 'Amiri', serif;
                    direction: rtl;
                }
            </style>
            <link href="https://fonts.googleapis.com/css2?family=Amiri&display=swap" rel="stylesheet">
        </head>
        <body>
            <div class="container">
                <div class="arabic-pattern">
                    <h1>Welcome to IslamicAI</h1>
                </div>
                <p>Hello John Doe,</p>
                <p>Thank you for joining IslamicAI. We're excited to have you onboard!</p>
                <p style="margin-bottom: 20px;">Getting started with our Islamic chatbot has never been easier.</p>
                <p>Your verification code is: <strong>123456</strong></p>
                <p>Please use this code to verify your account and unlock all the features of IslamicAI.</p>
                <p>If you have any questions or need assistance, feel free to reach out to our support team.</p>
                <p class="arabic-text">السلام عليكم</p>
            </div>
        </body>
        </html>
        """,
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
    assert "Welcome to IslamicAI" in email.body
