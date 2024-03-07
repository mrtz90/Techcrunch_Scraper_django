import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


app = Celery('scraper', broker='redis://localhost:6379/0')

# Load Celery settings from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Schedule the task to run every day at 9 o'clock
app.conf.beat_schedule = {
    'start-project-every-day-at-9': {
        'task': 'scraper.tasks.start_techcrunch_daily_scrape',
        'schedule': crontab(hour='15', minute='16'),
    },
}

app.autodiscover_tasks()
