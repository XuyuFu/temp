# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
import time

import PayFun.models
import PayFun.forms
# Create your views here.
def launch():
	if request.method == 'GET':
		context = { 'form': LaunchFrom() }
		return render(request, 'payfun/launch.html', context)

    launch_form = CreateForm(request.POST)
    if not create_form.is_valid():
    	context = { 'form': launch_form }
    	return render(request, 'payfun/launch.html', context)

    lauched_activity = Activity(launcher = request.user, post_time=timezone.now(), 
    	               is_lauch_success = False, is_hold_success = False, 
    	               is_start = False)
    launch_from = LaunchFrom(request.POST, instance = lauched_activity )

    if not launch_form.is_valid():
    	context = { 'form': launch_form }
    	return render(request, 'payfun/launch.html', context)

    launch_form.save()
    message = "You launch an activity"
    context = { 'message': message, 'activity': lauched_activity, 'form': launch_form }
    return render(request, 'PayFun/global.html', context)

