# scheduler.py

from extensions import scheduler, app
from email_service import process_leave_email

def register_jobs():  # 24 hour clock
    @scheduler.task(
        'cron',
        id='leave_email_daily',
        hour=16,
        minute=2
    )
    def scheduled_leave_mail():
        print("Running scheduled leave email job at 9:00 AM")

        with app.app_context():
            process_leave_email()
