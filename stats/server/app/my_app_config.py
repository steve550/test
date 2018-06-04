from threading import Thread

from django.apps import AppConfig
import schedule

from app.model.client import update_summary
import time


class MyAppConfig(AppConfig):
    name = 'app'
    verbose_name = "rannotate"
    def ready(self):
        print("App started...")
        #schedule.every(15).minutes.do(update_summary)
        #Thread(target=run_scheduler).start()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)
