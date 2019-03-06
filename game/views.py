import names
from django.db.models import Count
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from game.models import *


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = []


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['name']


def index(request, template_name='game/index.html'):
    if not request.session.session_key:
        request.session.save()
    data = dict()
    key = request.session.session_key
    return render(request, template_name, data)


def test(request, template_name='game/chat.html'):
    data = dict()
    return render(request, template_name, data)


def room_create(request):
    form = RoomForm(request.POST or None)
    if form.is_valid():
        form.save()
    return redirect('index')


def room_detail(request, pk, template_name='game/chat.html'):
    room = get_object_or_404(Room, pk=pk)
    data = dict()
    data['object'] = room
    return render(request, template_name, data)


def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.name = request.POST['name']
    if user.name.strip() != '':
        user.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)

