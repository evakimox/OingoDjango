from django.shortcuts import render, HttpResponse, render_to_response, HttpResponseRedirect

from mainsite.models import *


from django.contrib.auth import *
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
    if request.method == 'POST':
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
                except User.DoesNotExist:
                    if password == '':
                        errMsgPassword = 'Empty Password'
                    else:
                        user = User.objects.create_user(username, '', password)
                        user.save()
                        return HttpResponseRedirect('/register/success/')
    return render(request, 'register.html', {'username': username, 'errMsgUsername': errMsgUsername, 'errMsgPassword':errMsgPassword})


def login(request):
    '''
    if request.method == 'GET':
        form = LoginForm
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect(to='index')
            else:
                return HttpResponse("Not a user")

    '''

    return HttpResponse("login")




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



