from django.core.mail import send_mail
from .models import ScheduledEmail

def send_scheduled_emails():
    scheduled_emails = ScheduledEmail.objects.filter(is_sent=False)
    for email in scheduled_emails:
        send_mail(
            email.subject,
            email.message,
            email.recipient,
            [email.recipient],
            fail_silently=False,
        )
        email.is_sent = True
        email.save()
