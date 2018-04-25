# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.urls import reverse
from mimetypes import guess_type
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from payfun.models import Followed, Activity, Comment, Progress, ChatNotification
from payfun.models import Profile, SponserAndActivity, Notification
from payfun.forms import LaunchForm, ProfileForm, EditForm, ProgressForm
from .payment import payment
from .paydetails import paydetails
from .trans import trans
import pytz
import json
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import datetime
import requests
import collections
from nltk.tokenize import word_tokenize
from collections import Counter
import string

from googleplaces import GooglePlaces, types, lang
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

from django.db.models import Q


def login_page(request):
    return render(request,"login.html")

def tryLogin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        context = {}
        context['user'] = user
        activities = Activity.objects.all()

        all_notification = Notification.objects.filter(receiver=request.user)
        tag = False
        for notification in all_notification:
            if notification.read == False:
                tag = True

        context['has_unread'] = tag

        activity_groups = []
        temp_group = []

        for index, activity in enumerate(activities):
            if index % 3 == 0 and len(temp_group) != 0:
                activity_groups.append(temp_group)
                temp_group = []
                temp_group.append(activity)
            else:
                temp_group.append(activity)

        activity_groups.append(temp_group)
        context['activities'] = activity_groups

        return render(request, 'global.html', context)
        # return redirect(reverse('stream'))
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



    context = {}

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(first_name=request.POST.get('first_name'),
                                        last_name=request.POST.get('last_name'),
                                        username=request.POST.get('username'),
                                        password=request.POST.get('password'),
                                        email=request.POST.get('email'))
    new_user.is_active = False
    new_user.save()

    new_profile_entry = Profile(username=request.POST.get('username'), bio='default_bio', first_name=request.POST.get('first_name'),
                                 last_name=request.POST.get('last_name'))
    new_profile_entry.save()
    #
    # new_profile_form = ProfileForm(bio='default_bio', first_name=request.POST.get('first_name'),last_name=request.POST.get('last_name'))
    # if new_profile_form.is_valid():
    #     new_profile_form.save()

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

    # except Exception as e:
    #     context = {}
    #     print(str(e))
    # return render(request, 'signup.html', context)

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





@transaction.atomic
def launch(request):
    if request.method == 'GET':
        context = { 'form': LaunchForm() }
        return render(request, 'create_project.html', context)

    # launch_form = LaunchForm( content = request.POST.get('description'),location = request.POST.get('location'),
    # target_money = request.POST.get('target_money'),picture = request.POST.get('image'),title = request.POST.get('title'))


    # if not launch_form.is_valid():
    #     print("000")
    #     context = { 'form': launch_form}
    #     return render(request, 'launch.html', context)
    start_time =  request.POST.get('start_time')
    start_time_list = start_time.split('/')
    start_time = ''+ start_time_list[1] + ' ' + start_time_list[0]+ ' '+ start_time_list[2] + ' ' + '1:00AM'
    end_time   =  request.POST.get('end_time')
    end_time_list = end_time.split('/')
    end_time = ''+ end_time_list[1] + ' ' + end_time_list[0]+ ' '+ end_time_list[2] + ' ' + '1:00AM'

    start_time1 = datetime.strptime(start_time, '%m %d %Y %I:%M%p')
    end_time1 = datetime.strptime(end_time, '%m %d %Y %I:%M%p')

    print("----")
    user = request.user
    user_type = type(user)
    print("paypal email" + request.POST.get("paypal_email"))

    lauched_activity = Activity(content = request.POST.get('description'),location = request.POST.get('location'),
                                location_id=request.POST.get('location_id'), target_money=request.POST.get('target_money'),
                                picture=request.FILES['image'],title=request.POST.get('title'),launcher=request.user,
                                post_time=timezone.now(),start_time= start_time1,end_time= end_time1,is_end=False,
                                is_success=False, is_start=False, paypal_account=request.POST.get('paypal_email'))

    # launch_form_final = LaunchForm(request.POST, request.FILES)
    # if not launch_form_final.is_valid():
    #     print("1")
    # launch_form_final.save();

    # if not launch_form_final.is_valid():
    #     print("111")
    #     context = { 'form': launch_form_final }
    #     return render(request, 'create_project.html', context)
    print("222")
    lauched_activity.save()
    message = "You launch an activity"
    # all_activities = Activity.objects.all()
    # context = { 'message': message, 'activities': all_activities }
    # return render(request, 'global.html', context)
    all_activities = Activity.objects.all()

    activity_groups = []
    temp_group = []

    for index, activity in enumerate(all_activities):
        if index % 3 == 0 and len(temp_group) != 0:
            activity_groups.append(temp_group)
            temp_group = []
            temp_group.append(activity)
        else:
            temp_group.append(activity)

    activity_groups.append(temp_group)

    # return render(request, 'index.html', {'activities': all_activities})
    return render(request, 'global.html', {'activities': activity_groups})


@login_required
def activitydetail(request, activity_id):
    user_tmp = request.user
    username_tmp = request.user.username
    userlastname_tmp = user_tmp.last_name
    userfirstname_tmp = user_tmp.first_name

    Entry_Activity = get_object_or_404(Activity,id = activity_id)
    try:
        Entry_Profile     = Profile.objects.get(username = request.user.username)
    except:
        new_profile_entry = Profile(username= username_tmp,bio='default_bio',
                                    first_name= userfirstname_tmp,
                                    last_name= userlastname_tmp)
        new_profile_entry.save()
        Entry_Profile = get_object_or_404(Profile,username = request.user.username)
    if(request.user.username ==Entry_Activity.launcher.username):
        my_activity = '1'
    else:
        my_activity = '0'

    if Entry_Activity in Entry_Profile.follow_activity.all():
        activity_followed = '1'
    else:
        activity_followed = '0';



    return render(request, 'project_detail.html',{'activity':Entry_Activity, 'my_activity': my_activity,"activity_followed": activity_followed})

def groupByNum(elemList, num):
    result_groups = []
    temp_group = []

    for index, elem in enumerate(elemList):
        if index % num == 0 and len(temp_group) != 0:
            result_groups.append(temp_group)
            temp_group = []
            temp_group.append(elem)
        else:
            temp_group.append(elem)

    result_groups.append(temp_group)
    return result_groups

@login_required
def profile(request, user_name):
    if request.method == 'GET':

        user_tmp = request.user
        username_tmp = request.user.username
        userlastname_tmp = user_tmp.last_name
        userfirstname_tmp = user_tmp.first_name

        try:
            Entry = Profile.objects.get(username= user_name)
        except:
            new_profile_entry = Profile(username=user_name, bio='default_bio',
                                        first_name="default_first_name",
                                        last_name="default_last_name")
            new_profile_entry.save()
            Entry = get_object_or_404(Profile, username=user_name)

        if request.user.username == user_name :
            Edit_form = EditForm(instance = Entry)
            followees = Entry.followee.all()

            user = User.objects.get(username= user_name)
            activity_list = Activity.objects.filter(launcher= user)
            success_account1 = 0
            fail_account1 = 0
            for activity in activity_list:
                if activity.is_success == True:
                    success_account1 = success_account1 +1
                else :
                    fail_account1 = fail_account1 + 1

            followees = groupByNum(followees, 4)

            context = {
                'activity_list': activity_list,
                'success_account': success_account1,
                'fail_account': fail_account1,
                'entry':Entry,
                'form': Edit_form,
                'tag' :'1',
                'followees':followees,
                 }
            return render(request, 'profile.html', context)

        else:
            Profile_form = ProfileForm(instance = Entry)

            user = User.objects.get(username=user_name)
            activity_list = Activity.objects.filter(launcher=user)
            success_account1 = 0
            fail_account1 = 0
            for activity in activity_list:
                if activity.is_success == True:
                    success_account1 = success_account1 + 1
                else:
                    fail_account1 = fail_account1 + 1



            context = {
                'activity_list': activity_list,
                'success_account': success_account1,
                'fail_account': fail_account1,
                'entry':Entry,
                'form' :Profile_form,
                'tag':'0',
            }
            my_entry = Profile.objects.get(username = request.user.username)
            follow_user = User.objects.get(username = user_name)
            if follow_user in my_entry.followee.all():
                context['followma']='0'
            else:
                context['followma']='1'
            return render(request, 'profile.html', context)

    else:
        context = {}
        errors = []

        user_tmp = request.user
        username_tmp = request.user.username
        userlastname_tmp = user_tmp.last_name
        userfirstname_tmp = user_tmp.first_name

        try:
            entry = Profile.objects.get(username=user_name)
        except:
            new_profile_entry = Profile(username=user_name, bio='default_bio',
                                        first_name="default_first_name",
                                        last_name="default_last_name")
            new_profile_entry.save()
            entry = get_object_or_404(Profile, username=user_name)




        form  = EditForm (request.POST, request.FILES, instance=entry)

        user = User.objects.get(username=user_name)
        activity_list = Activity.objects.filter(launcher=user)
        success_account1 = 0
        fail_account1 = 0
        for activity in activity_list:
            if activity.is_success == True:
                success_account1 = success_account1 + 1
            else:
                fail_account1 = fail_account1 + 1



        if not form.is_valid():
            context['form'] = form
            context['message'] = 'Invalid input!'
            errors.append('You must enter text to add.')

        else:
            form.save()
            context = {
                        'activity_list': activity_list,
                        'success_account': success_account1,
                        'fail_account': fail_account1,
                        'message': 'Entry updated.',
                        'form' :form,
                        'entry':   entry,
                        'tag' :     '1',
                    }
        my_entry = Profile.objects.get(username = request.user.username)
        followees = my_entry.followee.all()
        followees = groupByNum(followees, 4)
        context['followees'] = followees
        context['error'] = errors
        return render(request, 'profile.html', context)


@login_required
def followUser(request, user_name):
    my_entry = get_object_or_404(Profile, username = request.user.username)
    follow_user = get_object_or_404(User, username = user_name)
    follow_entry = Profile.objects.get(username = user_name)

    my_entry.followee.add(follow_user)
    form = ProfileForm(instance = follow_entry)

    context = {
        'message': 'Successful Follow.',
        'form' :  form,
        'entry':  follow_entry,
        'tag'  :  '0',
        'followma': '0',
    }
    return render(request, 'profile.html', context)


@login_required
def unfollowUser(request, user_name):
    my_entry = get_object_or_404(Profile, username = request.user.username)
    follow_user = get_object_or_404(User, username = user_name)
    follow_entry = Profile.objects.get(username = user_name)

    my_entry.followee.remove(follow_user)
    form = ProfileForm(instance = follow_entry)

    context = {
        'message': 'Successful Follow.',
        'form' :  form,
        'entry':  follow_entry,
        'tag'  :  '0',
        'followma': '1',
    }
    return render(request, 'profile.html', context)

# @login_required
# def get_photo(request, user_name):
#     profile = get_object_or_404(Profile, username=user_name)
#     # Probably don't need this check as form validation requires a picture be uploaded.
#     if not profile.picture:
#         raise Http404
#     content_type= guess_type(profile.picture.name)
#     return HttpResponse(profile.picture, content_type=profile.content_type)

@login_required
def getPhoto(request, id):
    try:
        activity = Activity.objects.get(id=id)
        #profile = get_object_or_404(Profile, user=user)
         # item = get_object_or_404(Item, id=id)

        # Probably don't need this check as form validation requires a picture be uploaded.
        if not activity.picture:
            # raise Http404
            try:
                with open("default.png", "rb") as f:
                    return HttpResponse(f.read(), content_type="image/jpeg")
            except:
                raise Http404

        # return HttpResponse(profile.picture, content_type=profile.content_type)
        return HttpResponse(activity.picture, content_type="image/jpeg")
    except:
        # raise Http404
        try:
            with open("default.png", "rb") as f:
                return HttpResponse(f.read(), content_type="image/jpeg")
        except:
            raise Http404


@login_required
def add_comment(request):
    print("1111111111");
    if request.method != 'POST':
        raise Http404
    if not 'comment' in request.POST or not request.POST['comment']:
        message = 'You must enter a comment to add.'
        json_error = '{ "error": "'+message+'" }'
        return HttpResponse(json_error, content_type='application/json')

    time_str = request.POST['last_update_time']
    time_cur = timezone.localtime(timezone.now())
    cur_page = request.POST['cur_page']
    target_activity = Activity.objects.get(id = request.POST['activity_id'])
    new_comment = Comment(activity = target_activity, comment =request.POST['comment'],
                    commenter = User.objects.get(username=request.user.username), time= time_cur)
    new_comment.save()
    print("1111111111");
    response_data = get_update_data(time_str, new_comment.time,cur_page, target_activity.id)
    return HttpResponse(response_data, content_type='application/json')

@login_required
def add_progress(request):
    if request.method != 'POST':
        raise Http404
    if not 'progress' in request.POST or not request.POST['progress']:
        message = 'You must enter a comment to add.'
        json_error = '{ "error": "'+message+'" }'
        return HttpResponse(json_error, content_type='application/json')

    time_str = request.POST['last_update_time']
    print(time_str)
    cur_page = request.POST['cur_page']
    print(cur_page)
    target_activity = Activity.objects.get(id = request.POST['activity_id'])
    new_progress = Progress(activity = target_activity, content =request.POST['progress'],
                            time=timezone.localtime(timezone.now()))
    new_progress.save()

    followee_list = target_activity.followee.all()
    sponseree_list = target_activity.sponseree.all()

    for followee in followee_list:
        activity_tmp = target_activity
        receiver_tmp = followee
        notification_tmp = ""+ target_activity.title + "has new update"
        new_notification = Notification( activity = activity_tmp, receiver=receiver_tmp, notification_content = notification_tmp,time=timezone.now(),read=False)
        new_notification.save()
        notification_list = Notification.objects.filter(receiver= followee)
    for sponseree in sponseree_list:
        new_notification = Notification(activity=target_activity,receiver = sponseree, notification_content = ""+ target_activity.tile + "has new update",time=timezone.now(),read=False)
        new_notification.save()

    response_data = get_update_data(time_str, new_progress.time, cur_page, target_activity.id)

    return HttpResponse(response_data, content_type='application/json')

@login_required
def followActivity(request, activity_id):
    Entry_Activity = get_object_or_404(Activity, id = activity_id)
    Entry_Profile = get_object_or_404(Profile, username = request.user.username)

    Entry_Profile.follow_activity.add(Entry_Activity)
    Entry_Activity.followee.add(request.user)

    return render(request, 'project_detail.html',{'activity':Entry_Activity, 'my_activity': '0',"activity_followed": '1'})


@login_required
def unfollowActivity(request, activity_id):
    Entry_Activity = get_object_or_404(Activity, id = activity_id)
    Entry_Profile = get_object_or_404(Profile, username=request.user.username)

    Entry_Profile.follow_activity.remove(Entry_Activity)
    Entry_Activity.followee.remove(request.user)

    return render(request, 'project_detail.html',
                  {'activity': Entry_Activity, 'my_activity': '0', "activity_followed": '0'})


@login_required
def searchActivity(request):
    query = request.POST.get('searchInput')
    activities = Activity.objects.all()

    activity_groups = []
    temp_group = []

    activities = sortActivities(activities, query)

    for index, activity in enumerate(activities):
        if index % 3 == 0 and len(temp_group) != 0:
            activity_groups.append(temp_group)
            temp_group = []
            temp_group.append(activity)
        else:
            temp_group.append(activity)

    activity_groups.append(temp_group)
    return render(request, 'global.html', {'activities': activity_groups})

# rank all the activities
def sortActivities(activities, query):
    punctuations = list(string.punctuation)
    terms = word_tokenize(query)
    terms = [term for term in terms if term not in punctuations]
    content_weight = 0.5
    title_weight = 0.3
    author_weight = 0.2

    temp = []
    for activity in activities:
        score = 0
        for term in terms:
            content_score = getOccurences(activity.content, term) * content_weight
            title_score = getOccurences(activity.title, term) * title_weight
            author_score = getOccurences(activity.launcher.username, term) * author_weight
            score += content_score + title_score + author_score
        temp.append((activity, score))

    result = sorted(temp, key=lambda tup: tup[1], reverse=True)
    activities = []
    for tuple in result:
        activities.append(tuple[0])

    return activities

# get the occurences of a word in a string
def getOccurences(string, term):
    tokens = word_tokenize(string)
    cnt = Counter()
    for token in tokens:
        cnt[token] += 1

    if term in cnt:
        return cnt[term]
    else:
        return 0



def follow_stream(request):
    profile  = Profile.objects.get(username= request.user.username)
    all_activities = profile.follow_activity.all()
    return render(request, 'global.html', {'activities': all_activities})

def launched_stream(request):
    user = User.objects.get(username= request.user.username)
    all_activities = Activity.objects.filter(launcher = user)
    return render(request, 'global.html', {'activities': all_activities})

def get_update_data(time_str, time, cur_page, activity_id):
    time_format = "%Y-%m-%d %H:%M:%S.%f"

    latest_time = time.strftime(time_format)

    last_update_time = timezone.make_aware(datetime.strptime(time_str, time_format))

    if cur_page == '' or cur_page == 'global':
        update_posts = Activity.objects.filter(time__gt=last_update_time).order_by('time')
        update_comments = Comment.objects.filter(time__gt=last_update_time).order_by('time')
    elif cur_page == 'activitydetail' or cur_page == 'unfollowActivity' or cur_page =='followActivity':
    #     user_follow_entry = FollowEntry.objects.get(name=username)
    #     follow_list = user_follow_entry.followers.all()
    #     update_posts = PostEntry.objects.filter(name__in=follow_list).filter(time__gt=last_update_time).order_by('time')
    #     update_post_id = [i.id for i in PostEntry.objects.filter(name__in=follow_list)]
        related_activity = Activity.objects.get(id = activity_id)
        update_progress = Progress.objects.filter(activity=related_activity).filter(time__gt=last_update_time).order_by('time')
        update_comments = Comment.objects.filter(activity=related_activity).filter(time__gt=last_update_time).order_by('time')
    else:
        update_posts = []
        update_comments = []
        update_progress = []
    #update_post_data = list(map(lambda x: {'html':render_to_string('socialnetwork/post.html', context = {"post": x})}, update_posts))
    #response_post_data = json.dumps(update_post_data)


    update_progress_data = list(map(lambda x: {'html': render_to_string('progress.html',
                                                                       context={"progress": x}),
                                              'post_id': x.activity.id}, update_progress))
    update_comment_data = list(map(lambda x: {'html': render_to_string('comment.html',
                                                                       context={"comment": x}),
                                              'post_id': x.activity.id}, update_comments))


    response_comment_data = json.dumps(update_comment_data)
    response_progress_data = json.dumps(update_progress_data)

    data = {'last_update_time': latest_time, 'comments': response_comment_data, 'progress':response_progress_data}
    return json.dumps(data)

@login_required
def get_post_comment(request):
    time_str = request.GET['last_update_time']
    cur_page = request.GET['cur_page']
    activity_id = request.GET['activity_id']

    if time_str == 'Undefined':
        time_str = '1970-01-01 00:00:00.00'
    response_data = get_update_data(time_str, timezone.localtime(timezone.now()), cur_page, activity_id)
    return HttpResponse(response_data, content_type='application/json')

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')

def notification(request):
    notification_list = Notification.objects.filter(receiver= request.user)
    for notification in notification_list:
        notification.read = True
        notification.save()
    return render(request,'notifications.html', {'notifications':notification_list})

@login_required
def donations(request):
    context = {}
    return render(request, 'donations.html', context)

@login_required
def followings(request):
    # change this later

    activities = Activity.objects.all()

    activity_groups = []
    temp_group = []

    for index, activity in enumerate(activities):
        if index % 3 == 0 and len(temp_group) != 0:
            activity_groups.append(temp_group)
            temp_group = []
            temp_group.append(activity)
        else:
            temp_group.append(activity)

    activity_groups.append(temp_group)

    return render(request, 'global.html', {'activities' : activity_groups})

@login_required
def pay(request, activity_id):
    recipient_email = "fuxuyu-facilitator@outlook.com"
    # recipient_email = "fuxuyu-organizer@outlook.com"
    dollars = request.POST['t_amount']
    print(dollars)
    sponsor = request.user
    # activity = Activity.objects.filter(id=activity_id)
    activity = Activity.objects.get(id=activity_id)
    redirect_address, pay_key = payment(recipient_email, dollars)
    transaction = SponserAndActivity(sponsor=sponsor, activity=activity, money_amount=dollars, pay_key=pay_key)
    transaction.save()
    return redirect(redirect_address)

def transfer(recipient_email, dollars):
    # is there a problem? I think the dollars should be retrieved from the request parameters

    # Get the paypal redirect address from payment.py:
    print("transfer")
    # Get the paypal redirect address from payment.py:
    print("the email", recipient_email, "the amount", dollars)
    redirect_address = trans(recipient_email, dollars)
    # return redirect(redirect_address) 
    redirect(redirect_address)

    # payment(recipient_email, dollars)
    # return render(request, "paybutton.html")

@login_required
def refund(rpayKey, amount):
    # get the paykey and user from the corresponding database tables
    # how to get the sponser
    print("refund")
    email = paydetails(payKey)
    print("get the information")
    print("the email:", email, " the dollars:", amount)
    redirect_address = trans(email, amount)
    redirect(redirect_address)

@login_required()
def payhome(request):
    return render(request, "paybutton.html")


@login_required
def searchLocation(request):
    context = {}
    if 'query' in request.GET:
        YOUR_API_KEY = 'AIzaSyDZn-uP8j6Z3ugZTOVheG82DIGQTANS93U'
        google_places = GooglePlaces(YOUR_API_KEY)
        query_result = google_places.text_search(query=request.GET['query'], language=lang.ENGLISH,
            lat_lng=None, radius=3200,type=None, types=[], location=None, pagetoken=None)
        locations = []
        for place in query_result.places:
            one = {}
            one['name'] = place.name
            one['id'] = place.place_id
            place.get_details()
            one['address'] = place.formatted_address
            locations.append(one)
        context['locations'] = locations[0:5]
        return render(request, 'create_project.html', context)
    if 'choice' in request.POST:
        context['link'] = "https://www.google.com/maps/search/?api=1&query=any" + "&query_place_id=" + request.POST['choice-id']
        context['place_name'] = request.POST['choice']

        return render(request, 'create_project.html', context)
    else:
        return render(request, 'create_project.html', context)


def global_stream(request):
    # Gets a list of all the items in the todo-list database.
    activities = Activity.objects.all()
    activity_groups = []
    temp_group = []

    for index, activity in enumerate(activities):
        if index % 3 == 0 and len(temp_group) != 0:
            activity_groups.append(temp_group)
            temp_group = []
            temp_group.append(activity)
        else:
            temp_group.append(activity)

    activity_groups.append(temp_group)

    all_notification = Notification.objects.filter(receiver= request.user)
    tag = False
    for notification in all_notification:
        if notification.read == False:
            tag = True

    tag_chat = False
    chatNotifications = ChatNotification.objects.filter(read=False)
    if len(chatNotifications) != 0:
        tag_chat = True

    return render(request, 'global.html', {'activities': activity_groups, 'has_unread':tag, 'has_unread_chat':tag_chat})

    


@login_required
def get_all(request):
    cur_page = request.GET['cur_page']
    activity_id = request.GET['activity_id']

    related_activity = Activity.objects.get(id=activity_id)
    update_progress = Progress.objects.filter(activity=related_activity).order_by(
        'time')
    update_comments = Comment.objects.filter(activity=related_activity).order_by(
        'time')


    update_progress_data = list(map(lambda x: {'html': render_to_string('progress.html',
                                                                       context={"progress": x}),
                                              'post_id': x.activity.id}, update_progress))
    update_comment_data = list(map(lambda x: {'html': render_to_string('comment.html',
                                                                       context={"comment": x}),
                                              'post_id': x.activity.id}, update_comments))


    response_comment_data = json.dumps(update_comment_data)
    response_progress_data = json.dumps(update_progress_data)

    time = timezone.localtime(timezone.now())
    time_format = "%Y-%m-%d %H:%M:%S.%f"
    latest_time = time.strftime(time_format)


    data = {'last_update_time': latest_time, 'comments': response_comment_data, 'progress': response_progress_data}
    data1 = json.dumps(data)
    return HttpResponse(data1, content_type='application/json')

@login_required
def test(request):
    return render(request, 'test.html', {})

# return the chatting room
'''def room(request, room_name):
    return render(request, 'chat.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })'''

# return the chatting room
@login_required
def create_room(request, participant_name):
    participant = User.objects.get(username=participant_name)

    username = request.user.username
    room_name = username + '-' + participant_name

    try:
        chatNotification = ChatNotification.objects.get(room_id=room_name)
    except:
        chatNotification = ChatNotification(room_id=room_name, user1=request.user, user2=participant, read=False)
        chatNotification.save()

    chatNotifications = ChatNotification.objects.filter(Q(user1=request.user) | Q(user2=request.user))

    return render(request, 'test_chat.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'rooms': chatNotifications,
    })

@login_required
def room(request):
    chatNotifications = ChatNotification.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    return render(request, 'test_chat.html', {
        'rooms': chatNotifications,
    })

# the new chat bar
def test_chat(request):
    return render(request, 'test_chat.html', {})


def ratepage(request, notification_id):
    notification = Notification.objects.get(id= notification_id)
    return render(request,"rate.html",{"notification":notification})

def rate(request, notification_id):
    notification = get_object_or_404(Notification, id = notification_id)
    activity = notification.activity
    sponser_name = activity.launcher.username
    profile = get_object_or_404(Profile, username = sponser_name)
    rate_count = request.POST.get('rate')
    rate_count = int(rate_count)
    activity.total_rate = activity.total_rate + 1
    activity.rate_cur = ((activity.total_rate-1) * activity.rate_cur+ rate_count) / activity.total_rate
    if activity.rate_cur >= 3.0:
        activity.is_success = True
    else:
        activity.is_success = False
    activity.save()
    print(activity.rate_cur)
    print(activity.rate_cur)
    print(activity.rate_cur)
    print(activity.is_success)
    print(activity.is_success)
    print(activity.is_success)
    profile.total_rate = profile.total_rate+1
    profile.rate_cur = ((profile.total_rate - 1) * profile.rate_cur + rate_count ) / profile.total_rate
    profile.save()
    notification.has_rate = True
    notification.save()
    print(profile.rate_cur)
    print(profile.rate_cur)
    print(profile.rate_cur)


    activities = Activity.objects.all()
    activity_groups = []
    temp_group = []

    for index, activity in enumerate(activities):
        if index % 3 == 0 and len(temp_group) != 0:
            activity_groups.append(temp_group)
            temp_group = []
            temp_group.append(activity)
        else:
            temp_group.append(activity)

    activity_groups.append(temp_group)

    all_notification = Notification.objects.filter(receiver=request.user)
    tag = False
    for notification in all_notification:
        if notification.read == False:
            tag = True
    return render(request, 'global.html', {'activities': activity_groups, 'has_unread': tag})