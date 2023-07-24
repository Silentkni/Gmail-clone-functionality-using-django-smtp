import imaplib
import email




def fetch_emails():
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('syash5824@gmail.com', 'qeog rnfa rihe vdrw')

    # Select the mailbox you want to fetch emails from
    mail.select('INBOX')

    # Search for emails
    result, data = mail.search(None, 'ALL')

    emails = []

    # Iterate over the fetched emails
    for num in data[0].split():
        result, email_data = mail.fetch(num, '(RFC822)')

        # Parse the email data
        raw_email = email_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract relevant information
        subject = msg['subject']
        sender = msg['from']
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8')

        emails.append({
            'subject': subject,
            'sender': sender,
            'body': body,
        })

    # Close the connection
    mail.logout()

    return emails