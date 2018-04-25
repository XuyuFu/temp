# chat/urls.py
from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^test/', views.test, name='test'),
	url(r'^room/', views.room, name='room'),
    url(r'^(?P<participant_name>[^/]+)/$', views.create_room, name='create_room'),
]
