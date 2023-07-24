import imaplib
import email
from email.header import decode_header
import chardet
from app.models import Email
import time
import requests

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
    mail.login('syash5824@gmail.com', 'qeog rnfa rihe vdrw')

    # Select the mailbox (e.g., 'INBOX')
    mail.select('INBOX')

    # Retrieve the latest unread emails
    _, data = mail.search(None, 'UNSEEN')
    email_ids = data[0].split()

    for email_id in email_ids:
        _, data = mail.fetch(email_id, '(RFC822)')
        raw_email = data[0][1]  # Get the raw email content

        # Parse the raw email content
        msg = email.message_from_bytes(raw_email)

        # Extract the required email details
        sender = msg['From']
        subject, body = extract_main_text(msg)

        # Save the email to the database
        Email.objects.create(
            sender=sender,
            subject=subject,
            body=body
        )

    # Logout and close the IMAP connection
    mail.logout()

def fetch_and_reload_emails():
    # Fetch unread emails and save them to the database
    fetch_unread_emails()

    # Trigger a client-side refresh by sending a request to a URL
    # Modify the URL according to your Django project configuration
    # e.g., http://localhost:8000/refresh-inbox/
    # You can create a new Django view to handle this request and refresh the inbox page on the client-side
    refresh_url = 'http://localhost:8000/refresh-inbox/'
    requests.get(refresh_url)

# Run the initial fetch and reload
fetch_and_reload_emails()

# Schedule the job to fetch and reload emails every 5 minutes
while True:
    fetch_and_reload_emails()
    time.sleep(300)