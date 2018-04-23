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
from django.conf.urls import include

urlpatterns = [
    url(r'^$', views.login_page, name='login_page'),
    url(r'^login_page/$', views.login_page, name='login_page'),
    url(r'^login/$', views.tryLogin, name='login'),
    url(r'^signup/', views.signUp, name="signup"),
    url(r'^register/', views.register, name="register"),
    url(r'^stream/', views.global_stream, name="stream"),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9]+)/(?P<token>[a-z0-9\-]+)$',
        views.confirm_registration, name='confirm'),
    url(r'^launchactivity/$', views.launch, name="launCh"),
    url(r'^activitydetail/(?P<activity_id>\S+)/$', views.activitydetail, name="activityDetail"),
    # url(r'^.*$', RedirectView.as_view(pattern_name='login_page', permanent=False)),
    url(r'^profile/(?P<user_name>\S+)/$', views.profile, name='profile'),
    url(r'^followUser/(?P<user_name>\S+)$', views.followUser, name='followUser'),
    url(r'^unfollowUser/(?P<user_name>\S+)$', views.unfollowUser, name='unfollowUser'),
    # url(r'^photo/(?P<user_name>\S+)$', views.get_photo, name='photo'),
    url(r'^getPhoto/(?P<id>\d+)$', views.getPhoto, name='getPhoto'),
    url(r'^add-comment$', views.add_comment, name='addcomment'),
    url(r'^add-progress$', views.add_progress, name='addprogress'),
    url(r'^followActivity/(?P<activity_id>\S+)$', views.followActivity, name='followActivity'),
    url(r'^unfollowActivity/(?P<activity_id>\S+)$', views.unfollowActivity, name='unfollowActivity'),
    url(r'^searchActivity/$', views.searchActivity, name='searchActivity'),
    url(r'^donations/$', views.donations, name='donations'),
    url(r'^followings/$', views.followings, name='followings'),
    url(r'^get-post-comment$', views.get_post_comment),
    url(r'^global-stream$', views.global_stream, name="global"),
    url(r'^follow-stream$', views.follow_stream, name="follow"),
    url(r'^launched-stream$', views.launched_stream, name="launched"),
    url(r'^sponser-stream$', views.global_stream, name="global"),
    url(r'^transfer/', views.transfer, name="transfer"),
    url(r'^refund/(?P<activity_id>\S+)$', views.refund, name="refund"), # is there a problem here?
    url(r'^pay/(?P<activity_id>\S+)$', views.pay, name="pay"),
    url(r'^payhome$', views.payhome, name="payHome"),
    url(r'^searchLocation/', views.searchLocation, name="searchLocation"),
    # url(r'^.*$', RedirectView.as_view(pattern_name='login_page', permanent=False)),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^notifications/$', views.notification, name='notification'),
    url(r'^getAllProgressAndComment/$', views.get_all),
]
