# models.py
from django.db import models
import os

def get_attachment_path(instance, filename):
    # Modify the path to where you want to store the attachments
    return os.path.join('attachments', str(instance.email.id), filename)

class Email(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sender = models.EmailField()
    recipient = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    attachments_dir = models.CharField(max_length=255, blank=True, null=True)

    def _str_(self):
        return self.subject

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Save the attachments
        attachments_dir = os.path.join('media', 'attachments','2', str(self.id))
        os.makedirs(attachments_dir, exist_ok=True)

        for attachment in self.attachments.all():
            attachment_path = get_attachment_path(attachment, attachment.file.name)
            with open(attachment_path, 'wb') as file:
                file.write(attachment.file.read())

    def get_attachments(self):
        attachments_dir = os.path.join('media', 'attachments','2', str(self.id))
        if os.path.exists(attachments_dir):
            return os.listdir(attachments_dir)
        return []

class Attachment(models.Model):
    email = models.ForeignKey(Email, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_attachment_path)

    def _str_(self):
        return self.file.name