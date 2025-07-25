import os
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


scheduler = BackgroundScheduler()

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appsec_task'

    def ready(self):
        # Tránh chạy 2 lần trong môi trường dev (runserver autoreload)
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from appsec_task.views import send_reminder  # import từ views

		# Tránh scheduler bị thêm job 2 lần khi reload
        if not scheduler.get_jobs():
            scheduler.add_job(
                send_reminder,
                # CronTrigger(hour='*', minute='*'),
                CronTrigger(day_of_week='thu', hour=14, minute=0), #thứ 5 lúc 14h hàng tuần
				id="daily_reminder",
                replace_existing=True
            )

            scheduler.start()
            print("Scheduler started in apps.py")
