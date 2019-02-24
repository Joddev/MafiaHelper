from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('new', views.room_create, name='room_new'),
    path('room/<int:pk>', views.room_detail, name='room_detail'),
    url(r'^user/(?P<pk>\d+)/update/$', views.user_update, name='user_update'),
    url(r'^test/$', views.test, name='test'),
]
