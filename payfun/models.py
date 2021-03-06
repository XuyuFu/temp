from __future__ import unicode_literals


from django.db import models
from django.contrib.auth.models import User

# class User(models.Model):
# 	fullname = models.CharField(max_length=100)
# 	username = models.CharField(max_length=100)
# 	password = models.CharField(max_length=100)
# 	phone_number = models.CharField(max_length=100)
# 	email = models.CharField(max_length=100)
# 	# passPort = models.CharField(max_length=100)
# 	credits = models.FloatField()

class Activity(models.Model):
	#launcher = models.CharField(max_length=100)
	launcher = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=100)
	# brief_description = models.CharField(max_length=150)
	content = models.CharField(max_length=1000)
	picture = models.FileField(upload_to="images", blank=True)
	target_money = models.FloatField()
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	post_time = models.DateTimeField(auto_now_add=True)
	location = models.CharField(max_length=100)
	location_id = models.CharField(max_length=100)
	is_start = models.BooleanField() # whether the activity has started
	is_end = models.BooleanField() # whether the activity has failed, whether success or failure
	is_success = models.BooleanField(blank=True)
	followee = models.ManyToManyField(User, related_name='followeeForActivity')
	sponseree = models.ManyToManyField(User, related_name='sponsereeForActivity')
	paypal_account = models.CharField(max_length=1000)
	total_rate = models.IntegerField(default=0)
	rate_cur = models.FloatField(default=0)

# 	followee = models.ManyToManyField(User, related_name='followeeForActivity')
# 	sponseree = models.ManyToManyField(User, related_name='sponsereeForActivity')
# >>>>>>> 7e37414f9f910d65ebd0ad466c58d7e4fe644c12

class LauncherAndActivity(models.Model):
	launcher = models.ForeignKey(User, on_delete=models.CASCADE)
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

class SponserAndActivity(models.Model):
	sponsor = models.ForeignKey(User, on_delete=models.CASCADE)
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now_add=True)
	money_amount = models.FloatField()
	# the pay key is used for refund
	pay_key = models.CharField(max_length=50)

class Followed(models.Model):
 	user = models.ForeignKey(User, on_delete=models.CASCADE)
 	activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

class Progress(models.Model):
 	activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
 	time = models.DateTimeField(auto_now_add=True) # the time at which the progress is made
 	content = models.CharField(max_length=150)
 	picture = models.FileField(upload_to="images", blank=True)

class Comment(models.Model):
 	activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
 	commenter = models.ForeignKey(User, on_delete=models.CASCADE)
 	comment = models.CharField(max_length=150)
 	time = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
	receiver = models.ForeignKey(User, on_delete=models.CASCADE)
	notification_content = models.CharField(max_length=150)
	time = models.DateTimeField()
	read = models.BooleanField()
	has_rate = models.BooleanField(default=False)

class ChatNotification(models.Model):
	room_id = models.CharField(max_length=100)
	user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
	user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')
	time = models.DateTimeField(auto_now_add=True)
	read = models.BooleanField()

class ChatLog(models.Model):
	room_id = models.CharField(max_length=100)
	message = models.CharField(max_length=100)
	time = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
	username         = models.CharField(max_length=40)
	first_name       = models.CharField(max_length=40,default="")
	last_name        = models.CharField(max_length=40,default="")
	bio              = models.CharField(max_length=40)
	followee         = models.ManyToManyField(User, related_name='followee')
	follow_activity  = models.ManyToManyField(Activity, related_name="follow_activity")
	launch_activity = models.ManyToManyField(Activity, related_name="launch_activity")
	sponser_activity = models.ManyToManyField(Activity, related_name="sponser_activity")
	picture          = models.FileField(upload_to="images", blank=True)
	content_type     = models.CharField(max_length=50,default="")
	total_rate = models.IntegerField(default=0)
	rate_cur = models.FloatField(default=0)



