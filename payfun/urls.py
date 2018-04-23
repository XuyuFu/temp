# chat/urls.py
from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^test/', views.test, name='test'),
    url(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),
]
