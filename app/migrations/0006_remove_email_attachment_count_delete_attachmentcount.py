# Generated by Django 4.2.3 on 2023-07-20 06:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_email_attachment_count_attachmentcount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='email',
            name='attachment_count',
        ),
        migrations.DeleteModel(
            name='AttachmentCount',
        ),
    ]
