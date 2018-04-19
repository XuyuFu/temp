# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from payfun.models import Followed, Activity, Comment
import pytz
import json
from datetime import datetime
from django.utils import timezone
import time

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
'''config = {
    'apiKey': "AIzaSyCU1lWMaRDwgkL1p-n6-kHxeDsvGK7Y1Gw",
    'authDomain': "payfun-4a679.firebaseapp.com",
    'databaseURL': "https://payfun-4a679.firebaseio.com",
    'projectId': "payfun-4a679",
    'storageBucket': "",
    'messagingSenderId': "127339190594"
}
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()'''

def login_page(request):
    return render(request,"login.html")

def tryLogin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        context = {}
        context['user'] = user
        return render(request, 'global.html', context)
    else:
        # Return an 'invalid login' error message.
        return render(request, 'login.html')

def signUp(request):
    return render(request, 'signup.html')

# Create your views here.
@transaction.atomic
def register(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        # context['form'] = RegistrationForm()
        return render(request, 'signup.html', context)

    try:
        with transaction.atomic():
            # Creates a bound form from the request POST parameters and makes the
            # form available in the request context dictionary.
            # form = RegistrationForm(request.POST)
            # context['form'] = form
            context = {}

            # At this point, the form data is valid.  Register and login the user.
            temp = request.POST.get('fullname')
            new_user = User.objects.create_user(first_name=request.POST.get('first_name'),
                                                last_name=request.POST.get('last_name'),
                                                username=request.POST.get('username'),
                                                password=request.POST.get('password'),
                                                email=request.POST.get('email'))
            new_user.is_active = False
            new_user.save()

            # new_profile = Profile(user=new_user)
            # new_profile.save()

            # Generate a one-time use token and an email message body
            token = default_token_generator.make_token(new_user)

            email_body = """
Please click the link below to verify your email address and
complete the registration of your account:

  http://{host}{path}
""".format(host=request.get_host(), 
           path=reverse('confirm', args=(new_user.username, token)))
    
            send_mail(subject="Verify your email address",
                      message= email_body,
                      from_email="yuanweic@cmu.edu",
                      recipient_list=[new_user.email])

            # context['email'] = form.cleaned_data['email']
            context['email'] = request.POST.get('email')

            return render(request, 'needs_confirmation.html', context)

    except Exception as e:
        context = {}
        print(str(e))
        return render(request, 'signup.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()

    return render(request, 'confirmed.html', {})

def stream(request):
    context = {}
    return render(request, 'global.html', context)

@login_required
@transaction.atomic
## there are still some changes to be made
def followOthers(request, userId):
    try:
        userFollowed = User.objects.get(id=userId)

        following = Followed(user1=request.user,
                             user2=userFollowed)
        following.save()
    except:
        error = 'some error happens!!'
        context = {}
        context["isGlobal"] = True
        return render(request, 'stream.html', context)

    # return redirect(reverse('profile'), userId=userId)
    return redirect(reverse('detail', args=(userId,)))

@login_required
@transaction.atomic
# change this later
def unfollow(request, userId):
    try:
        userFollowed = User.objects.get(id=userId)
        following = Followed.objects.get(user1=request.user,
                                         user2=userFollowed)
        following.delete()
    except:
        error = 'Object does not exist'

    # return redirect(reverse('profile'), userId=userId)
    return redirect(reverse('detail', args=(request.user.id,)))

@login_required
@transaction.atomic
def addComment(request):
    data = []

    try:
        with transaction.atomic():
            if 'activity_id' in request.POST and 'text' in request.POST:
                activityId = request.POST['post_id']
                activity = Activity.objects.get(id=activityId)
                comment = Comment(comment=request.POST['comment'],
                                  commenter=request.user,
                                  activity=activity)
                comment.save()
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')


    # return redirect(reverse('getCommentsJson'), request)

    utc = pytz.UTC

    context = {}
    # need to add some contexts here

    return render(request, 'project_detail.html', context)



    '''if "most_recent_date" not in request.POST:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    mostRecentDateStr = request.POST["most_recent_date"]
    try:
        mostRecentDate = datetime.strptime(mostRecentDateStr, "%m %d, %Y %H:%M:%S")
        mostRecentDate = utc.localize(mostRecentDate)
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    posts = Post.objects.all().order_by('created').reverse()

    for post in posts:
        try:
            comments = Comment.objects.filter(post=post).order_by('created')
            # comments.append(temp)
            for comment in comments:

                commentTime = comment.created.strftime("%m %d, %Y %H:%M:%S")
                commentTimeDate = datetime.strptime(commentTime, "%m %d, %Y %H:%M:%S")
                commentTimeDate = utc.localize(commentTimeDate)

                if commentTimeDate > mostRecentDate:
                    data.append({"post_id": post.id, "commented_by_id": comment.user.id,
                                 "commented_by_name": comment.user.username,
                                 "created": comment.created.strftime("%m %d, %Y %H:%M:%S"),
                                 "text": comment.text})

        except Comment.DoesNotExist:
            continue

    responseJson = json.dumps(data)
    return HttpResponse(responseJson, content_type='application/json')'''

