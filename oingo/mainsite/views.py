from django.shortcuts import render, HttpResponse, HttpResponseRedirect, Http404

from mainsite.models import *

from django.utils import timezone
import django.contrib.auth as auth
from django.contrib.auth.models import User
from django.db.models import Q

from .form import *

import itertools


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
                        return HttpResponseRedirect('/account/register/success/')
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
                        return HttpResponseRedirect('/account/login/success/')
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


def account_profile_redirect(request):
    user = login_status(request)
    if user is not None:
        return HttpResponseRedirect('/account/profile/' + user.username + '/')
    else:
        return HttpResponseRedirect('/account/login/')


# to be modified - personal profile
def account_profile(request, profile_username):
    user = login_status(request)
    try:
        profile_user = User.objects.get(username=profile_username)
    except User.DoesNotExist:
        raise Http404("User does not exist!")
    else:
        if request.method == 'GET':
            user_self = 0
            friend_status = 0
            if user is not None:  # logged in status
                if user.username == profile_username:  # show the profile page of yourself!
                    user_self = 1
                else:   # show other's profile page
                    user_self = 0
                    try:
                        friend = Friend.objects.get(friender=user.id, friendee=profile_user.id)
                    except Friend.DoesNotExist:
                        try:
                            friend = Friend.objects.get(friender=profile_user.id, friendee=user.id)
                        except Friend.DoesNotExist:  # doesnt have any request
                            friend_status = 0
                        else: # profile send request to user
                            if friend.confirmed:
                                friend_status = 3
                            else:
                                friend_status = 2
                    else:  # user send request to profile
                        if friend.confirmed:
                            friend_status = 3
                        else:
                            friend_status = 1
            else: # logged out status, show someone's profile page, without logged in
                user_self = -1
        elif request.method == 'POST':
            if user is not None:
                if user.username == profile_username:  # show the profile page of yourself!
                    user_self = 1
                    return HttpResponse('Cannot friend yourself', status=403)
                else:   # show other's profile page
                    user_self = 0
                req = request.POST.get('friend')
                if req == 'Friend':
                    try:
                        friend = Friend.objects.get(friender=user.id, friendee=profile_user.id)
                    except Friend.DoesNotExist:
                        try:
                            friend = Friend.objects.get(friender=profile_user.id, friendee=user.id)
                        except Friend.DoesNotExist:  # doesnt have any request
                            friend = Friend(friender=user.id,
                                            friendee=profile_user.id,
                                            comfirmed=False,
                                            createtime=timezone.now())
                            friend.save()
                            friend_status = 1
                        else:
                            return HttpResponse('Already Exist friend record', status=403)
                    else:
                        return HttpResponse('Already Exist friend record', status=403)
                elif req == 'Confirm':
                    try:
                        friend = Friend.objects.get(friender=profile_user.id, friendee=user.id)
                    except Friend.DoesNotExist:  # doesnt have any request
                        return HttpResponse('No request can be found', status=403)
                    friend.confirmed = True
                    friend.save()
                    friend_status = 3
            else:
                return HttpResponse('Not logged in', status=401)
    return render(request, 'account_profile.html',
           {'profile_username': profile_username, 'user_self': user_self, 'friend_status': friend_status})


def account_settings(request):
    user = login_status(request)
    if user is None:
        return HttpResponseRedirect('/')
    err_msg_password = ''
    last_password = ''
    new_password = ''
    if request.method == 'GET':
        return render(request, 'account_settings.html', {'errMsgPassword': err_msg_password})
    elif request.method == 'POST':
        form = PasswordForm(request.POST)
        last_password = request.POST.get('last_password')
        new_password = request.POST.get('new_password')
        if form.is_valid():
            if last_password == '':
                err_msg_password = 'Pleas enter your original password'
            else:
                if new_password == '':
                    err_msg_password = 'Please enter your new password'
                else:
                    user = auth.authenticate(username=user.username, password=last_password)
                    if user is None:
                        err_msg_password = 'Invalid original password!'
                    else:
                        user.set_password(new_password)
                        user.save()
                        auth.login(request, user)
                        err_msg_password = 'Successfully Changed Password!'
    return render(request, 'account_settings.html', {'errMsgPassword': err_msg_password})


def friend_list(request):
    user = login_status(request)
    if user is None:
        return HttpResponseRedirect('/account/login/')
    user_friend_list = itertools.chain(
        User.objects.filter(Q(ufriender__confirmed=True), Q(ufriender__friendee=user.id)),
        User.objects.filter(Q(ufriendee__confirmed=True), Q(ufriendee__friender=user.id))
    )
    return render(request, 'friend_list.html', {'user_friend_list': user_friend_list})


def friend_request(request):
    user = login_status(request)
    if user is None:
        return HttpResponseRedirect('/account/login/')
    if request.method == 'GET':
        requester_user_friend_list = User.objects.filter(Q(ufriendee__confirmed=False), Q(ufriendee__friender=user.id))
        requestee_user_friend_list = User.objects.filter(Q(ufriender__confirmed=False), Q(ufriender__friendee=user.id))
    if request.method == 'POST':
        friend_id = list(request.POST.keys())[list(request.POST.values()).index('Confirm')]
        try:
            friend = Friend.objects.get(friender=friend_id, friendee=user.id)
        except Friend.DoesNotExist:
            return HttpResponse('No request can be found', status=403)
        friend.confirmed = True
        friend.save()
        return HttpResponseRedirect('/account/friend/request/')
    return render(request, 'friend_request.html', {'requester_user_friend_list': requester_user_friend_list,
                                                   'requestee_user_friend_list': requestee_user_friend_list})


def filter_list(request):
    return HttpResponse("filterlist")


def filter_create(request):
    return HttpResponse("filtercreate")


def filter_settings(request, fid):
    return HttpResponse("filtersettings" + fid)


def note(requset, note_id):
    return HttpResponse("note" + note_id)




def create_note(request):
    tags = Tag.objects.all()
    Tags = {'TagList': tags}
    return render(request, "writeNote.html", Tags)


def create_tag(request):
    return render(request, "createTag.html")


def submit_tag(request):
    if request.method == 'POST':
        newTag = request.POST.get('newTag')
        tag = Tag(ttext=newTag)
        tag.save()
        print("priting new tag id:",  tag.tid)
        return HttpResponse("Your tag is saved")
    else:
        return HttpResponse("Sorry there is some error")


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def submit_note(request):
    if request.method == 'POST':
        noteText = request.POST.get('noteText')
        user = login_status(request)
        if user is None:
            return HttpResponseRedirect('/account/login/')
        lat = request.POST.get('displayLat')
        lng = request.POST.get('displayLog')
        if (not is_float(lat)) or (not is_float(lng)):
            return HttpResponse("The location is not correct, please select on map and re-try :) ")
        radius = request.POST.get('radius')
        if not is_float(radius):
            return HttpResponse("The radius you give I cannot understand, would you try another one?")
        starttime = request.POST.get('startTime')
        endtime = request.POST.get('endTime')
        visibleDate = request.POST.get('visibleDate')

        starttime = visibleDate + ' ' + starttime
        endtime = visibleDate + ' ' + endtime

        visibility = request.POST.get('visibleType')
        createtime = timezone.now()
        myNote = Note(uid=user,
                      ntext=noteText,
                      lat=lat, lng=lng, radius=radius,
                      starttime=starttime,
                      endtime=endtime,
                      scheduletype=1,
                      visibility=visibility,
                      createtime=createtime)

        selectedTags = request.POST.getlist("selectDefaultTags")
        myNote.save()
        notetagBulk = []
        if len(selectedTags)>0:
            for tag in selectedTags:
                notetag = NoteTag(nid_id=myNote.nid, tid_id=tag)
                notetagBulk.append(notetag)
            NoteTag.objects.bulk_create(notetagBulk)
        return HttpResponse(noteText)

