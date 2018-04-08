from __future__ import unicode_literals


from django.db import models
from django.contrib.auth.models import User

class User(models.Model):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	username = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	phone_number = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	# passPort = models.CharField(max_length=100)
	credits = models.FloatField()

class Activity(models.Model):
	#launcher = models.CharField(max_length=100)
	launcher = models.ForeignKey(User)
	title = models.CharField(max_length=100)
	# brief_description = models.CharField(max_length=150)
	content = models.CharField(max_length=1000)
	picture = models.FileField(upload_to="images", blank=True)
	target_money = models.FloatField()
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	post_time = models.DateTimeField(auto_now_add=True)
	location = models.CharField(max_length=100)
	is_start = models.BooleanField() # whether the activity has started
	is_end = models.BooleanField() # whether the activity has failed, whether success or failure
	is_success = models.BooleanField(blank=True)

class LauncherAndActivity(models.Model):
	launcher = models.ForeignKey(User)
	activity = models.ForeignKey(Activity)

class SponserAndActivity(models.Model):
	sponsor = models.ForeignKey(User)
	activity = models.ForeignKey(Activity)
	time = models.DateTimeField(auto_now_add=True)
	money_amount = models.FloatField()
	is_anonymous = models.BooleanField()

class Followed(models.Model):
 	user = models.ForeignKey(User)
 	activity = models.ForeignKey(Activity)

class Progress(models.Model):
 	activity = models.ForeignKey(Activity)
 	time = models.DateTimeField(auto_now_add=True) # the time at which the progress is made
 	content = models.CharField(max_length=150)
 	picture = models.FileField(upload_to="images", blank=True)

class Comment(models.Model):
 	activity = models.ForeignKey(Activity)
 	commenter = models.ForeignKey(User)
 	comment = models.CharField(max_length=150)
 	time = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
 	activity = models.ForeignKey(Activity)
 	sponsor = models.ForeignKey(User)
 	notification = models.CharField(max_length=150)
 	time = models.DateTimeField()