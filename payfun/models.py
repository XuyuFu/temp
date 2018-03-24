# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Data model for a post
class Post(models.Model):
	header = models.CharField(max_length=200)
	text = models.CharField(max_length=1000)
	user = models.ForeignKey(User, default=None)
	created = models.DateTimeField(auto_now_add=True)

# Data model for a profile
class Profile(models.Model):
	bio = models.CharField(max_length=1000)
	joined = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, default=None)
	picture = models.FileField(upload_to="images", blank=True)


# Data model for people I followed
class Following(models.Model):
	user1 = models.ForeignKey(User, related_name='user1', default=None)
	user2 = models.ForeignKey(User, related_name='user2', default=None)

# Data model for comment
class Comment(models.Model):
	text = models.CharField(max_length=1000)
	user = models.ForeignKey(User, default=None)
	created = models.DateTimeField(auto_now_add=True)
	post = models.ForeignKey(Post, default=None)
