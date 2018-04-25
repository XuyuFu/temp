# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils import timezone


class PayfunConfig(AppConfig):
    name = 'payfun'

    def ready(self):

        def job():
            print("haha")
            import datetime
            from .views import transfer
            from .views import refund
            from payfun.models import Followed, Activity, Comment, Progress
            from payfun.models import Profile, SponserAndActivity, Notification
            for activity in Activity.objects.filter(start_time__lte=(datetime.datetime.now() + datetime.timedelta(days=1)),
                                                 start_time__gt=datetime.datetime.now()):
                sum = 0
                for sponsor in SponserAndActivity.objects.filter(activity__exact=activity):
                    sum = sum + sponsor.money_amount
                if sum >= activity.target_money:
                    # activity.is_hold_success = true
                    print("in apps the sum", sum)
                    transfer(activity.paypal_account, sum)
                else:
                    # activity.is_hold_success = false
                    for sponsor in SponserAndActivity.objects.filter(activity__exact=activity):
                        print(sponsor.pay_key)
                        refund(sponsor.pay_key, sponsor.money_amount)
            # for activity in Activity.objects.filter(end_time__gte=(datetime.datetime.now() - datetime.timedelta(days=1)),
            #                                      end_time__lt=datetime.datetime.now()):
            #     for sponsor in SponserAndActivity.objects.filter(activity__exact=activity):
            #         Notification(activity=target_activity, receiver=sponseree,
            #                      notification_content="" + target_activity.tile + "has new update", time=timezone.now(),
            #                      read=False)
            #         new_notification.save()

            print("2222")
            activity_list = Activity.objects.filter(end_time__gte=(datetime.datetime.now() - datetime.timedelta(days=1)),
                                                  end_time__lt=datetime.datetime.now())
            print("-----")
            print(activity_list)
            print(len(activity_list))
            print("------")

            for activity in activity_list:
                sponserAndActivity_list = SponserAndActivity.objects.filter(activity__exact=activity)
                print("-----")
                print((sponserAndActivity_list))
                print("-----")
                print(len(sponserAndActivity_list))
                print("-----")

                for sponsorAndActivity_per in sponserAndActivity_list:
                    new_notification= Notification(activity=activity, receiver= sponsorAndActivity_per.sponsor,
                                  notification_content="" + activity.title + "has finished, come here for rate! <a href =/ratepage/" + str(activity.id) +"/>link</a>", time=timezone.now(),
                                  read=False)
                    new_notification.save()
                    print(new_notification)
                    print(new_notification.activity)
                    print(new_notification.receiver.username)
                    print(new_notification.notification_content)

        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        print("to add")
        # scheduler.add_job(job, 'cron', day='1-30', hour=00, minute=29)
        scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=23, minute=5)
        #scheduler.add_job(job, 'interval', seconds=10)
        scheduler.start()
        