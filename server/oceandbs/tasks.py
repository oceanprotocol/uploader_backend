from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from .models import Storage

# Simple scheduled tasks to run every minutes which checks when a storage service is more than 10 minutes old, and if so, set it to inactive
def remove_expired_storage():
  date_check=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
  storages = Storage.objects.filter(created__lte=date_check)
  for storage in storages:
    storage.is_active = False

def start():
  sched = BackgroundScheduler()
  sched.add_job(remove_expired_storage, 'cron', minute='*')
  sched.start()