from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from .models import Storage

# Simple scheduled tasks to run every minutes which checks when a storage service is more than 10 minutes old, deletes it
def remove_expired_storage():
  date_check=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
  Storage.objects.filter(created__lte=date_check).delete()

def start():
  sched = BackgroundScheduler()
  sched.add_job(remove_expired_storage, 'cron', minute='*')
  sched.start()