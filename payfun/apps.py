# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class PayfunConfig(AppConfig):
    name = 'payfun'

    def ready(self):

        def job():
            from .views import transfer
            from .views import refund
            now = timezone.now()
            for activity in Activity.objects.get(start_time__lte=(datetime.datetime.now() + datetime.timedelta(days=1)),
                                                 start_time__gt=datetime.datetime.now()):
                sum = 0
                for sponsor in SponserAndActivity.objects.get(activity__exact=activity):
                    sum = sum + sponsor.money_amount
                if sum >= activity.target_money:
                    # activity.is_hold_success = true
                    # transfer(activity.organizer_email, sum)
                    transfer("fuxuyu-buyer@outlook.com", sum)
                else:
                    # activity.is_hold_success = false
                    for sponsor in SponserAndActivity.objects.get(activity__exact=activity):
                        refund(sponsor.payKey)
            for activity in Activity.objects.get(end_time__gte=(datetime.datetime.now() - datetime.timedelta(days=1)),
                                                 end_time__lt=datetime.datetime.now()):
                for sponsor in SponserAndActivity.objects.get(activity__exact=activity):
                    notification(activity=target_activity, receiver=sponseree,
                                 notification_content="" + target_activity.tile + "has new update", time=timezone.now(),
                                 read=False)
                    new_notification.save()


        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(job, 'cron', day='1-30', hour=23, minute=59)
        scheduler.start()
    
       