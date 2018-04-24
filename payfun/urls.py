# chat/urls.py
from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^test/', views.test, name='test'),
	url(r'^test_chat/', views.test_chat, name='test_chat'),
    url(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),
]
