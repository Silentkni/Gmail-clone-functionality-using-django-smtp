from django_cron import CronJobBase, Schedule
from app.views import fetch_unread_emails


class FetchUnreadEmailsCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # run every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.Fetch_unread_emails_cron_Job'  # a unique code for your cron job

def do(self):
        # Your code for refreshing the inbox
    fetch_unread_emails()  # Call your email fetching function"""