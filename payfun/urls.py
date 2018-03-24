"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from payfun import views
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', auth_views.login, {'template_name':'payfun/login.html'}, name='login'),
    url(r'^login$', auth_views.login, {'template_name':'payfun/login.html'}, name='login'),
    url(r'^profile(?P<userId>\w+)$', views.profile, name='profile'),
    url(r'^register$', views.register, name='register'),
    url(r'^stream$', views.stream, name='stream'),
    url(r'^getPostsJson$', views.getPostsJson, name='getPostsJson'),
    url(r'^getCommentsJson$', views.getCommentsJson, name='getCommentsJson'),
    url(r'^getFollowerPostsJson$', views.getFollowerPostsJson, name='getFollowerPostsJson'),
    url(r'^getFollowerCommentsJson$', views.getFollowerCommentsJson, name='getFollowerCommentsJson'),
    url(r'^followerStream$', views.followerStream, name='followerStream'),
    url(r'^logout$', auth_views.logout,  {'next_page': 'login'}, name='logout'),
    url(r'^add-post$', views.addPost, name='add-post'),
    url(r'^add-comment$', views.addComment, name='add-comment'),
    url(r'^editProfile$', views.editProfile, name='editProfile'),
    url(r'^getPhoto/(?P<id>\d+)$', views.getPhoto, name='getPhoto'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9]+)/(?P<token>[a-z0-9\-]+)$',
        views.confirm_registration, name='confirm'),
    # url(r'^add-comment/(?P<postId>\w+)$', views.addComment, name='add-comment'),
    url(r'^followOthers/(?P<userId>\w+)$', views.followOthers, name='followOthers'),
    url(r'^unfollow/(?P<userId>\w+)$', views.unfollow, name='unfollow'),
    url(r'^.*$', RedirectView.as_view(pattern_name='login', permanent=False)),
]
