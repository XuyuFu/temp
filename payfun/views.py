from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from itertools import chain

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core import serializers
from django.core.mail import send_mail
from django.db import transaction
# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

import pytz
import json
from datetime import datetime

from payfun.forms import *
from payfun.models import *

# Create your views here.
@transaction.atomic
def register(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'payfun/register.html', context)

    try:
        with transaction.atomic():
            # Creates a bound form from the request POST parameters and makes the
            # form available in the request context dictionary.
            form = RegistrationForm(request.POST)
            context['form'] = form

            # Validates the form.
            if not form.is_valid():
                return render(request, 'payfun/register.html', context)

            # At this point, the form data is valid.  Register and login the user.
            new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                                password=form.cleaned_data['password1'],
                                                first_name=form.cleaned_data['first_name'],
                                                last_name=form.cleaned_data['last_name'],
                                                email=form.cleaned_data['email'])
            new_user.is_active = False
            new_user.save()

            new_profile = Profile(user=new_user)
            new_profile.save()

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

            context['email'] = form.cleaned_data['email']

            return render(request, 'payfun/needs-confirmation.html', context)

    except:
        context['form'] = RegistrationForm()
        return render(request, 'payfun/register.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()

    # Logs in the new user and redirects to his/her global stream page
    # new_user = authenticate(username=form.cleaned_data['username'],
    #                         password=form.cleaned_data['password1'])
    # login(request, new_user)
    # return redirect(reverse(''))

    return render(request, 'payfun/confirmed.html', {})


@login_required
def stream(request):
    # sort the list
    '''posts = Post.objects.all().order_by('created').reverse()
    
    pairs = []
    comments = []
    for post in posts:
        # pairs[post] = []
        try:
            temp = Comment.objects.filter(post=post).order_by('created').reverse()
            comments.append(temp)
        except Comment.DoesNotExist:
            continue

    pairs = zip(posts, comments)
    context = {'pairs':pairs}'''
    context = {}
    context["isGlobal"] = True
    return render(request, 'payfun/stream.html', context)

@login_required
def followerStream(request):
    # sort the list
    # posts = Post.objects.order_by('-created')
    '''pairs = {}

    try:
        myFollows = Following.objects.filter(user1=request.user)
    except:
        context = {'pairs':pairs}
        return render(request, 'socialnetwork/stream.html', context)

    posts = []
    for myFollow in myFollows:
        # posts.extend(list(Post.objects.filter(user=myFollow.user2).order_by('-created')))
        posts = chain(posts, (Post.objects.filter(user=myFollow.user2).order_by('created').reverse().all()))
    posts = sorted(posts, key=lambda x: x.created, reverse=True)
    
    comments = []
    for post in posts:
        try:
            temp = Comment.objects.filter(post=post).order_by('created').reverse()
            comments.append(temp)
        except Comment.DoesNotExist:
            continue

    pairs = zip(posts, comments)
    context = {'pairs':pairs}'''
    context = {}
    context["isGlobal"] = False

    return render(request, 'payfun/stream.html', context)

'''@login_required
def addPost(request):
    new_post = Post(header=request.POST['header'],
                    text=request.POST['text'],
                    user=request.user)
    new_post.save()

    posts = Post.objects.order_by('created').reverse()

    pairs = {}
    
    comments = []
    for post in posts:
        try:
            temp = Comment.objects.filter(post=post).order_by('created').reverse()
            comments.append(temp)
        except Comment.DoesNotExist:
            continue

    pairs = zip(posts, comments)
    context = {'pairs':pairs}
    return render(request, 'socialnetwork/stream.html', context)'''

@login_required
@transaction.atomic
def addPost(request):
    data = []

    try:
        with transaction.atomic():
            if 'header' in request.POST and 'text' in request.POST:
                new_post = Post(header=request.POST['header'],
                            text=request.POST['text'],
                            user=request.user)
                new_post.save()
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')


    utc = pytz.UTC

    # get the most recent date
    if "most_recent_date" not in request.POST:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    mostRecentDateStr = request.POST["most_recent_date"]
    try:
        mostRecentDate = datetime.strptime(mostRecentDateStr, "%m %d, %Y %H:%M:%S")
        mostRecentDate = utc.localize(mostRecentDate)
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    posts = Post.objects.all().order_by('created')

    for post in posts:

        postTime = post.created.strftime("%m %d, %Y %H:%M:%S")
        postTimeDate = datetime.strptime(postTime, "%m %d, %Y %H:%M:%S")
        postTimeDate = utc.localize(postTimeDate)

        if postTimeDate > mostRecentDate:
            postItem = {}
            postItem["post_id"] = post.id
            postItem["header"] = post.header
            postItem["posted_by_id"] = post.user.id
            postItem["posted_by_name"] = post.user.username
            postItem["created"] = post.created.strftime("%m %d, %Y %H:%M:%S")
            postItem["text"] = post.text
            data.append(postItem)

    responseJson = json.dumps(data)
    return HttpResponse(responseJson, content_type='application/json')




@login_required
def profile(request, userId):
    try:
        user = User.objects.get(id=userId)
        user_profile = Profile.objects.get(user=user)
    except:
        return redirect(reverse('stream'))

    isLoggedinUser = False
    ifFollow = True
    if user_profile.user == request.user:
        isLoggedinUser = True
    else:
        try:
            following = Following.objects.get(user1=request.user,
                                          user2=user)
            ifFollow = True
        except:
            ifFollow = False

    myFollows = []
    try:
        records = Following.objects.filter(user1=user)
        temp = []

        count = 0

        for myFollow in records:
            if count % 3 == 0:
                myFollows.append(temp)
                temp = []
                temp.append(myFollow)
                count = count + 1
            else:
                temp.append(myFollow)
                count = count + 1
        myFollows.append(temp)
    except:
        error = 'Object does not exist'

    form = EditForm()

    context = {'user_profile':user_profile, 'isLoggedinUser':isLoggedinUser, 'ifFollow':ifFollow,
        'myFollows':myFollows, 'followNum':count, 'form':form}
    return render(request, 'payfun/profile.html', context)

'''@login_required
def addComment(request, postId):
    context = {}

    post = Post.objects.get(id=postId)
    comment = Comment(text=request.POST['text'],
                      user=request.user,
                      post=post)
    comment.save()

    return redirect(reverse('stream'))'''

@login_required
@transaction.atomic
def addComment(request):
    data = []

    try:
        with transaction.atomic():
            if 'post_id' in request.POST and 'text' in request.POST:
                postId = request.POST['post_id']
                post = Post.objects.get(id=postId)
                comment = Comment(text=request.POST['text'],
                                user=request.user,
                                post=post)
                comment.save()
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')


    # return redirect(reverse('getCommentsJson'), request)

    utc = pytz.UTC

    if "most_recent_date" not in request.POST:
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
    return HttpResponse(responseJson, content_type='application/json')



@login_required
@transaction.atomic
def followOthers(request, userId):
    try:
        userFollowed = User.objects.get(id=userId)

        following = Following(user1=request.user,
                            user2=userFollowed)
        following.save()
    except:
        error = 'some error happens!!'
        context = {}
        context["isGlobal"] = True
        return render(request, 'payfun/stream.html', context)

    # return redirect(reverse('profile'), userId=userId)
    return redirect(reverse('profile', args=(userId,)))

@login_required
@transaction.atomic
def unfollow(request, userId):
    try:
        userFollowed = User.objects.get(id=userId)
        following = Following.objects.get(user1=request.user,
                                          user2=userFollowed)
        following.delete()
    except:
        error = 'Object does not exist'

    # return redirect(reverse('profile'), userId=userId)
    return redirect(reverse('profile', args=(request.user.id,)))

@login_required
@transaction.atomic
def editProfile(request):

    try:
        instance = get_object_or_404(Profile, user=request.user)
        form = EditForm(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            form.save()
    except:
        error = 'Error happend!'

    return redirect(reverse('profile', args=(request.user.id,)))

@login_required
def getPhoto(request, id):
    try:
        user = User.objects.get(id=id)
        profile = get_object_or_404(Profile, user=user)
         # item = get_object_or_404(Item, id=id)

        # Probably don't need this check as form validation requires a picture be uploaded.
        if not profile.picture:
            # raise Http404
            try:
                with open("default.png", "rb") as f:
                    return HttpResponse(f.read(), content_type="image/jpeg")
            except:
                raise Http404

        # return HttpResponse(profile.picture, content_type=profile.content_type)
        return HttpResponse(profile.picture, content_type="image/jpeg")
    except:
        # raise Http404
        try:
            with open("default.png", "rb") as f:
                return HttpResponse(f.read(), content_type="image/jpeg")
        except:
            raise Http404

@login_required
def getPostsJson(request):
    data = []

    utc = pytz.UTC

    # get the most recent date
    if "most_recent_date" not in request.GET:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    mostRecentDateStr = request.GET["most_recent_date"]

    try:
        mostRecentDate = datetime.strptime(mostRecentDateStr, "%m %d, %Y %H:%M:%S")
        mostRecentDate = utc.localize(mostRecentDate)
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    posts = Post.objects.all().order_by('created')

    for post in posts:

        postTime = post.created.strftime("%m %d, %Y %H:%M:%S")
        postTimeDate = datetime.strptime(postTime, "%m %d, %Y %H:%M:%S")
        postTimeDate = utc.localize(postTimeDate)

        if postTimeDate > mostRecentDate:
            postItem = {}
            postItem["post_id"] = post.id
            postItem["header"] = post.header
            postItem["posted_by_id"] = post.user.id
            postItem["posted_by_name"] = post.user.username
            postItem["created"] = post.created.strftime("%m %d, %Y %H:%M:%S")
            postItem["text"] = post.text
            data.append(postItem)

    responseJson = json.dumps(data)
    return HttpResponse(responseJson, content_type='application/json')

@login_required
def getCommentsJson(request):
    data = []

    utc = pytz.UTC

    if "most_recent_date" not in request.GET:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    mostRecentDateStr = request.GET["most_recent_date"]

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
    return HttpResponse(responseJson, content_type='application/json')


@login_required
def getFollowerCommentsJson(request):
    data = []

    try:
        myFollows = Following.objects.filter(user1=request.user)
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    posts = []
    for myFollow in myFollows:
        # posts.extend(list(Post.objects.filter(user=myFollow.user2).order_by('-created')))
        posts = chain(posts, (Post.objects.filter(user=myFollow.user2).order_by('created').reverse().all()))
    posts = sorted(posts, key=lambda x: x.created)

    utc = pytz.UTC

    if "most_recent_date" not in request.GET:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    mostRecentDateStr = request.GET["most_recent_date"]

    try:
        mostRecentDate = datetime.strptime(mostRecentDateStr, "%m %d, %Y %H:%M:%S")
        mostRecentDate = utc.localize(mostRecentDate)
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

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
    return HttpResponse(responseJson, content_type='application/json')


@login_required
def getFollowerPostsJson(request):
    # sort the list
    # posts = Post.objects.order_by('-created')
    data = []

    try:
        myFollows = Following.objects.filter(user1=request.user)
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    posts = []
    for myFollow in myFollows:
        # posts.extend(list(Post.objects.filter(user=myFollow.user2).order_by('-created')))
        posts = chain(posts, (Post.objects.filter(user=myFollow.user2).order_by('created').reverse().all()))
    posts = sorted(posts, key=lambda x: x.created)

    utc = pytz.UTC

    if "most_recent_date" not in request.GET:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    mostRecentDateStr = request.GET["most_recent_date"]

    try:
        mostRecentDate = datetime.strptime(mostRecentDateStr, "%m %d, %Y %H:%M:%S")
        mostRecentDate = utc.localize(mostRecentDate)
    except:
        responseJson = json.dumps(data)
        return HttpResponse(responseJson, content_type='application/json')

    for post in posts:

        postTime = post.created.strftime("%m %d, %Y %H:%M:%S")
        postTimeDate = datetime.strptime(postTime, "%m %d, %Y %H:%M:%S")
        postTimeDate = utc.localize(postTimeDate)

        if postTimeDate > mostRecentDate:
            postItem = {}
            postItem["post_id"] = post.id
            postItem["header"] = post.header
            postItem["posted_by_id"] = post.user.id
            postItem["posted_by_name"] = post.user.username
            postItem["created"] = post.created.strftime("%m %d, %Y %H:%M:%S")
            postItem["text"] = post.text
            data.append(postItem)

    responseJson = json.dumps(data)
    return HttpResponse(responseJson, content_type='application/json')
