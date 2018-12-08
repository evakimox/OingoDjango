from django.shortcuts import render, HttpResponse, render_to_response, HttpResponseRedirect

from mainsite.models import *


import django.contrib.auth as auth
from django.contrib.auth.models import User

from .form import *

# Create your views here.

def index(request):
    return HttpResponse("index")


def registerSuccess(request):
    return HttpResponse("register success")


def register(request):
    errMsgUsername = ''
    errMsgPassword = ''
    username = ''
    password = ''
    if request.method == 'GET':
        if loginStatus(request) is not None:   # already logged in?
            return HttpResponseRedirect('/')
        else:
            return render(request, 'register.html', {'username': username, 'errMsgUsername': errMsgUsername, 'errMsgPassword':errMsgPassword})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        if form.is_valid():
            if username == '':
                errMsgUsername = 'Please enter your username'
            elif len(username) > 10:
                errMsgUsername = 'Username too long'
            else:
                try:
                    User.objects.get(username=username)
                    errMsgUsername = 'Username already exists'
                except User.DoesNotExist:
                    if password == '':
                        errMsgPassword = 'Empty Password'
                    else:
                        user = User.objects.create_user(username, '', password)
                        user.save()
                        user = auth.authenticate(username=username, password=password)
                        return HttpResponseRedirect('/register/success/')
    return render(request, 'register.html', {'username': username, 'errMsgUsername': errMsgUsername, 'errMsgPassword':errMsgPassword})


def loginSuccess(request):
    return HttpResponse("login success")


def login(request):
    errMsgUsername = ''
    errMsgPassword = ''
    username = ''
    password = ''
    if request.method == 'GET':
        if loginStatus(request) is not None:   # already logged in?
            return HttpResponseRedirect('/')
        else:
            return render(request, 'login.html', {'username': username, 'errMsgUsername': errMsgUsername, 'errMsgPassword':errMsgPassword})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        if form.is_valid():
            if username == '':
                errMsgUsername = 'Pleas enter your username'
            else:
                try:
                    User.objects.get(username=username)
                except User.DoesNotExist:
                    errMsgUsername = 'Invalid username'
                else:
                    user = auth.authenticate(username=username, password=password)
                    if user is not None and user.is_active:
                        auth.login(request, user)
                        return HttpResponseRedirect('/login/success/')
                    elif user is not None and not user.is_active:
                        errMsgPassword = 'Not an active user!'
                    else:
                        errMsgPassword = 'Wrong password'
    return render(request, 'login.html', {'username': username, 'errMsgUsername': errMsgUsername, 'errMsgPassword':errMsgPassword})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')



def loginStatus(request):
    if request.user.is_authenticated and request.user.is_active:
        return request.user
    else:
        return None




def note(requset, nid):
    return HttpResponse("note" + nid)




def friendlist(request):
    return HttpResponse("friendlist")



def friendrequest(request):
    return HttpResponse("friendrequest")




def createnote(request):
    return HttpResponse("createnote")



def filterlist(request):
    return HttpResponse("filterlist")

def filtercreate(request):
    return HttpResponse("filtercreate")

def filtersettings(request, fid):
    return HttpResponse("filtersettings" + fid)



