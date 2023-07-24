from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from app.models import Email, Attachment
from django.core.mail import EmailMessage
import imaplib
from email.parser import BytesParser
from email.header import decode_header
import chardet
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import login
import os
from django.conf import settings
from django.http import HttpResponse
import mimetypes
from django.contrib.auth.decorators import login_required

#from django.http import HttpResponse
#import schedule
#import time

def authentication_required(view_func):
    decorated_view_func = login_required(view_func)
    return decorated_view_func

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inbox')
            else:
                error_message = 'Password is incorrect.'
                return render(request, 'app/login.html', {'form': form, 'error_message': error_message})
    else:
        form = AuthenticationForm(request)

    return render(request, 'app/login.html', {'form': form})

@login_required
def sent_emails(request):
    # Fetch the latest 5 sent emails from the database
    emails = Email.objects.filter(is_sent=True).order_by('-timestamp')[:5]
    return render(request, 'app/sent_emails.html', {'emails': emails})


def extract_main_text(msg):
    # Decode the subject
    subject = msg['Subject']
    decoded_subject = decode_header(subject)[0][0]
    if isinstance(decoded_subject, bytes):
        decoded_subject = decoded_subject.decode()

    # Extract the plain text body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                payload = part.get_payload(decode=True)
                encoding = part.get_content_charset()
                if encoding:
                    try:
                        body = payload.decode(encoding)
                    except UnicodeDecodeError:
                        detected_encoding = chardet.detect(payload)
                        body = payload.decode(detected_encoding['encoding'])
                else:
                    detected_encoding = chardet.detect(payload)
                    body = payload.decode(detected_encoding['encoding'])
                break
    else:
        payload = msg.get_payload(decode=True)
        encoding = msg.get_content_charset()
        if encoding:
            try:
                body = payload.decode(encoding)
            except UnicodeDecodeError:
                detected_encoding = chardet.detect(payload)
                body = payload.decode(detected_encoding['encoding'])
        else:
            detected_encoding = chardet.detect(payload)
            body = payload.decode(detected_encoding['encoding'])

    return decoded_subject, body

def fetch_unread_emails():
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL('imap.gmail.com')

    # Login to the email account
    mail.login('gniot.priyanka.2m@gmail.com', 'kfck irha ydho myko')

    # Select the mailbox (e.g., 'INBOX')
    mail.select('INBOX')

    # Retrieve the latest unread emails
    _, data = mail.search(None, 'UNSEEN')
    email_ids = data[0].split()

    for email_id in email_ids:
        _, data = mail.fetch(email_id, '(RFC822)')
        raw_email = data[0][1]  # Get the raw email content

        # Parse the raw email content
        msg = BytesParser().parsebytes(raw_email)

        # Extract the required email details
        sender = msg['From']
        subject, body = extract_main_text(msg)

        # Create a directory to store attachments for this email
        attachments_dir = os.path.join(settings.MEDIA_ROOT, 'attachments', f'{email_id}')
        os.makedirs(attachments_dir, exist_ok=True)

        # Save the email to the database
        emailModalObj = Email.objects.create(
            sender=sender,
            subject=subject,
            body=body,
            attachments_dir=attachments_dir
        )
        # Iterate over the email parts to find attachments
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue

            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()

            # Save the attachment file
            if filename:
                filepath = os.path.join(attachments_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                
                # emailModalObj.attachments.create(file=filename)
                Attachment.objects.create(
                    file=filename,
                    email=emailModalObj
                )


    # Logout and close the IMAP connection
    mail.logout()


@login_required
def inbox(request):
    # Fetch unread emails and save them to the database
    fetch_unread_emails()

    # Fetch the latest emails from the database
    emails = Email.objects.order_by('-timestamp')[:5]

    return render(request, 'app/inbox.html', {'emails': emails})

"""def download_attachment(request, email_id, attachment_name):
    email = get_object_or_404(Email, id=email_id)
    attachment_path = os.path.join('media', email.attachments_dir, attachment_name)
    with open(attachment_path, 'rb') as file:
        response = HttpResponse(file.read())
        content_type = mimetypes.guess_type(attachment_path)[0]
        response['Content-Type'] = content_type
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(attachment_name)
        return response"""

@login_required
def view_attachments(request, email_id):
    email = get_object_or_404(Email, pk=email_id)
    attachments = email.get_attachments()
    return render(request, 'app/attachments.html', {'attachments': attachments})


@login_required
def compose(request):
    return render(request, 'app/compose.html')

@login_required
def send_email(request):
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        attachment = request.FILES.get('attachment')  # Retrieve the attachment file

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email='gniot.priyanka.2m@gmail.com',
            to=[recipient],
        )

        if attachment:
            email.attach(attachment.name, attachment.read(), attachment.content_type)

        try:
            email.send()

            # Save the sent email to the database
            Email.objects.create(
                subject=subject,
                body=body,
                sender='gniot.priyanka.2m@gmail.com',
                recipient=recipient,
                is_sent=True
            )

            messages.success(request, 'Email sent successfully.')
        except Exception as e:
            messages.error(request, 'An error occurred while sending the email.')

        return redirect('inbox')

    return render(request, 'app/compose.html')

"""@login_required
def read_email(request, email_id):
    email = get_object_or_404(Email, pk=email_id)
    attachments = email.attachments.all()
    return render(request, 'app/read_email.html', {'email': email, 'attachments': attachments})"""

def read_email(request, email_id):
    email = get_object_or_404(Email, pk=email_id)
    attachments = email.attachments.all()
    return render(request, 'app/read_email.html', {'email': email, 'attachments': attachments})



@login_required
def delete_email(request, email_id):
    email = get_object_or_404(Email, pk=email_id)

    if request.method == 'POST':
        email.delete()
        return redirect('inbox')

    return redirect('inbox')

@login_required
def forward_email(request, email_id):
    email = get_object_or_404(Email, pk=email_id)

    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')

        send_mail(
            subject=email.subject,
            message=email.body,
            from_email=email.sender,
            recipient_list=[recipient_email],
        )

        return redirect('inbox')

    return redirect('inbox')