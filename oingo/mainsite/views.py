from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from mainsite.models import *


import django.contrib.auth as auth
from django.contrib.auth.models import User

from .form import *


def index(request):
    return HttpResponse("index")


def register_success(request):
    return render(request, 'register_success.html')


def register(request):
    err_msg_username = ''
    err_msg_password = ''
    username = ''
    password = ''
    if request.method == 'GET':
        if login_status(request) is not None:   # already logged in?
            return HttpResponseRedirect('/')
        else:
            return render(request, 'register.html',
                          {'username': username, 'errMsgUsername': err_msg_username, 'errMsgPassword':err_msg_password})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        if form.is_valid():
            if username == '':
                err_msg_username = 'Please enter your username'
            elif len(username) > 10:
                err_msg_username = 'Username too long'
            else:
                try:
                    User.objects.get(username=username)
                    err_msg_username = 'Username already exists'
                except User.DoesNotExist:
                    if password == '':
                        err_msg_password = 'Empty Password'
                    else:
                        user = User.objects.create_user(username, '', password)
                        user.save()
                        user = auth.authenticate(username=username, password=password)
                        return HttpResponseRedirect('/register/success/')
    return render(request, 'register.html',
                  {'username': username, 'errMsgUsername': err_msg_username, 'errMsgPassword':err_msg_password})


def login_success(request):
    return render(request, 'login_success.html')


def login(request):
    err_msg_username = ''
    err_msg_password = ''
    username = ''
    password = ''
    if request.method == 'GET':
        if login_status(request) is not None:   # already logged in?
            return HttpResponseRedirect('/')
        else:
            return render(request, 'login.html',
                          {'username': username, 'errMsgUsername': err_msg_username, 'errMsgPassword':err_msg_password})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        if form.is_valid():
            if username == '':
                err_msg_username = 'Pleas enter your username'
            else:
                try:
                    User.objects.get(username=username)
                except User.DoesNotExist:
                    err_msg_username = 'Invalid username'
                else:
                    user = auth.authenticate(username=username, password=password)
                    if user is not None and user.is_active:
                        auth.login(request, user)
                        return HttpResponseRedirect('/login/success/')
                    elif user is not None and not user.is_active:
                        err_msg_password = 'Not an active user!'
                    else:
                        err_msg_password = 'Wrong password'
    return render(request, 'login.html',
                  {'username': username, 'errMsgUsername': err_msg_username, 'errMsgPassword':err_msg_password})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def login_status(request):
    if request.user.is_authenticated and request.user.is_active:
        return request.user
    else:
        return None


def note(requset, nid):
    return HttpResponse("note" + nid)


def friend_list(request):
    return HttpResponse("friendlist")


def friend_request(request):
    return HttpResponse("friendrequest")


def create_note(request):
    return HttpResponse("createnote")


def filter_list(request):
    return HttpResponse("filterlist")


def filter_create(request):
    return HttpResponse("filtercreate")


def filter_settings(request, fid):
    return HttpResponse("filtersettings" + fid)



