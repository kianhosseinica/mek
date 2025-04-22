# emails.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_test_email(recipient, user):
    """
    Sends a test email using an HTML template.
    'user' is an instance of your CustomUser.
    """
    subject = "Test Email from Django"

    # Render plain text as fallback
    message = render_to_string('store/test_email.txt', {'user': user})
    # Render HTML version of the email
    html_message = render_to_string('store/test_email.html', {'user': user})

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [recipient],
        html_message=html_message,
        fail_silently=False,
    )


# store/emails.py
# store/emails.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

import logging

logger = logging.getLogger(__name__)


def send_receipt_email(order):
    subject = f"Your Receipt for Order #{order.id}"
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    try:
        message = render_to_string('store/receipt_email.txt', context)
        html_message = render_to_string('store/receipt_email.html', context)
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [order.user.email]

        send_mail(subject, message, from_email, recipient_list, html_message=html_message, fail_silently=False)
        logger.info(f"Receipt email sent for order #{order.id} to {order.user.email}")
    except Exception as e:
        logger.error(f"Error sending receipt email for order #{order.id}: {e}")
        raise



from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def send_verification_code_email(email, code):
    subject = "Your 4-Digit Verification Code"
    context = {"code": code}
    message = render_to_string('store/verification_email.txt', context)
    html_message = render_to_string('store/verification_email.html', context)

    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )




