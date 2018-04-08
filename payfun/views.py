# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
import time
import pyrebase

# import PayFun.models
# import PayFun.forms
# Create your views here.
# def launch():
# 	if request.method == 'GET':
# 		context = { 'form': LaunchFrom() }
# 		return render(request, 'payfun/launch.html', context)

#     launch_form = CreateForm(request.POST)
#     if not create_form.is_valid():
#     	context = { 'form': launch_form }
#     	return render(request, 'payfun/launch.html', context)

#     lauched_activity = Activity(launcher = request.user, post_time=timezone.now(), 
#     	               is_lauch_success = False, is_hold_success = False, 
#     	               is_start = False)
#     launch_from = LaunchFrom(request.POST, instance = lauched_activity )

#     if not launch_form.is_valid():
#     	context = { 'form': launch_form }
#     	return render(request, 'payfun/launch.html', context)

#     launch_form.save()
#     message = "You launch an activity"
#     context = { 'message': message, 'activity': lauched_activity, 'form': launch_form }
#     return render(request, 'PayFun/global.html', context)
config = {
    'apiKey': "AIzaSyCU1lWMaRDwgkL1p-n6-kHxeDsvGK7Y1Gw",
    'authDomain': "payfun-4a679.firebaseapp.com",
    'databaseURL': "https://payfun-4a679.firebaseio.com",
    'projectId': "payfun-4a679",
    'storageBucket': "",
    'messagingSenderId': "127339190594"
}
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

def logIn(request):
    return render(request,"login.html")

def postsign(request):
    email = request.POST.get('email')
    passw = request.POST.get('password')
    try:
        user = authe.sign_in_with_email_and_password(email, passw)
    except:
    	print("11111111111111111111111111111")
    	message = "invalid credential"
    	return render(request,"login.html",{"messg":message})
    # session_id = user['idToken']
    # request.session['uid'] = str(session_id)
    return render(request,"index.html",{"e":email})


def signUp(request):
    return render(request, 'signup.html')


def postsignup(request):
    fullname = request.POST.get('fullname')
    username = request.POST.get('username')
    email = request.POST.get('email')
    passw = request.POST.get('password')
    try:
        authe.send_email_verification(user['idToken'])
        # user = authe.create_user_with_email_and_password(email,passw)
    except:
        message = "Email is already registed"
        return  render(request, "signup.html", {"messg":message})
    

    uid = user['localId']

    data={"fullname":fullname,"username":username,"status":"1"}

    results = database.child("users").child(uid).push(data, user['idToken'])
    print(user['idToken'])
    print(user['idToken'])
    print(user['idToken'])

    message = "register successfully"
    return render(request, "login.html", {"messg":message})

# Create your views here.
@transaction.atomic
def launch():
    if request.method == 'GET':
        context = { 'form': LaunchFrom() }
        return render(request, 'payfun/launch.html', context)

    launch_form = CreateForm(request.POST)
    if not create_form.is_valid():
        context = { 'form': launch_form }
        return render(request, 'payfun/launch.html', context)

    lauched_activity = Activity(launcher = request.user, is_lauch_success = False, is_hold_success = False, 
                       is_start = False)
    launch_from = LaunchFrom(request.POST, instance = lauched_activity )

    if not launch_form.is_valid():
        context = { 'form': launch_form }
        return render(request, 'payfun/launch.html', context)

    launch_form.save()
    message = "You launch an activity"
    context = { 'message': message, 'activity': lauched_activity, 'form': launch_form }
    return render(request, 'PayFun/global.html', context)
