#!/usr/bin/env python3
from typing import Dict, List

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email(
    subject: str,
    recipient_list: List[str],
    template_name: str,
    context: Dict,
    from_email=None,
):
    """Sends an email using the specified HTML template and context.

    :param subject: str
    :param recipient_list: list
    :param template_name: str
    :param context: dict
    :param rendered: in the template
    :param from_email: str (Default value = None)
    :param Defaults: to settings
    :param subject: str:
    :param recipient_list: List[str]:
    :param template_name: str:
    :param context: Dict:
    :param subject: str: 
    :param recipient_list: List[str]: 
    :param template_name: str: 
    :param context: Dict: 
    :returns: None

    """
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER

    # Render HTML content
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    # Create email message
    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
