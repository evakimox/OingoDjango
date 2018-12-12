from django.shortcuts import render, HttpResponse, HttpResponseRedirect, Http404

from mainsite.models import *

from django.utils import timezone
import django.contrib.auth as auth
from django.contrib.auth.models import User
from django.db.models import Q
from .form import *

import itertools
import time
import datetime
from geopy.distance import great_circle


def index(request):
    return HttpResponseRedirect('/timeline/')


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
            elif len(username) > 20:
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


def account_profile(request, profile_username):
    user = login_status(request)
    if user is None:
        user_status = False
        user_username = None
    else:
        user_status = True
        user_username = user.username

    states = []
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
                    states = State.objects.filter(uid=user)

                else:   # show other's profile page
                    user_self = 0
                    try:
                        friend = Friend.objects.get(friender_id=user.id, friendee_id=profile_user.id)
                    except Friend.DoesNotExist:
                        try:
                            friend = Friend.objects.get(friender_id=profile_user.id, friendee_id=user.id)
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
            else:  # logged out status, show someone's profile page, without logged in
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
                        friend = Friend.objects.get(friender_id=user.id, friendee_id=profile_user.id)
                    except Friend.DoesNotExist:
                        try:
                            friend = Friend.objects.get(friender_id=profile_user.id, friendee_id=user.id)
                        except Friend.DoesNotExist:  # doesnt have any request
                            friend = Friend(friender_id=user.id,
                                            friendee_id=profile_user.id,
                                            confirmed=False,
                                            createtime=timezone.now())
                            friend.save()
                            friend_status = 1
                        else:
                            return HttpResponse('Already Exist friend record', status=403)
                    else:
                        return HttpResponse('Already Exist friend record', status=403)
                elif req == 'Confirm':
                    try:
                        friend = Friend.objects.get(friender_id=profile_user.id, friendee_id=user.id)
                    except Friend.DoesNotExist:  # doesnt have any request
                        return HttpResponse('No request can be found', status=403)
                    friend.confirmed = True
                    friend.save()
                    friend_status = 3
            else:
                return HttpResponse('Not logged in', status=401)
    return render(request, 'account_profile.html',
           {'profile_username': profile_username, 'user_self': user_self, 'friend_status': friend_status,
            'states': states, 'user_status': user_status, 'user_username': user_username})


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
            friend = Friend.objects.get(friender_id=friend_id, friendee_id=user.id)
        except Friend.DoesNotExist:
            return HttpResponse('No request can be found', status=403)
        friend.confirmed = True
        friend.save()
        return HttpResponseRedirect('/account/friend/request/')
    return render(request, 'friend_request.html', {'requester_user_friend_list': requester_user_friend_list,
                                                   'requestee_user_friend_list': requestee_user_friend_list})


def create_note(request):
    user = login_status(request)
    if user is None:
        return HttpResponseRedirect('/account/login/')
    tags = Tag.objects.all()
    user_username = user.username
    return render(request, "writeNote.html", {'TagList': tags, 'user_username': user_username})


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

        starttime = datetime.datetime.strptime(visibleDate + ' ' + starttime, "%Y-%m-%d %H:%M")
        endtime = datetime.datetime.strptime(visibleDate + ' ' + endtime, "%Y-%m-%d %H:%M")
        starttime = datetime.datetime.fromtimestamp(starttime.timestamp() - 5 * 60 * 60)
        endtime = datetime.datetime.fromtimestamp(endtime.timestamp() - 5 * 60 * 60)

        visibility = request.POST.get('visibleType')
        createtime = timezone.now()
        myNote = Note(
            uid=user,
            ntext=noteText,
            lat=lat, lng=lng, radius=radius,
            starttime=starttime,
            endtime=endtime,
            scheduletype=1,
            visibility=visibility,
            createtime=createtime
        )

        selectedTags = request.POST.getlist("selectDefaultTags")
        myNote.save()
        notetagBulk = []
        if len(selectedTags)>0:
            for tag in selectedTags:
                notetag = NoteTag(nid_id=myNote.nid, tid_id=tag)
                notetagBulk.append(notetag)
            NoteTag.objects.bulk_create(notetagBulk)
        return HttpResponseRedirect("/")


def display(ctime, ltime, rtime, scheduletype):
    ctime = ctime.timestamp()
    ltime = ltime.timestamp() + 5 * 60 * 60
    rtime = rtime.timestamp() + 5 * 60 * 60
    c = time.localtime(ctime)
    l = time.localtime(ltime)
    r = time.localtime(rtime)
    ct = c.tm_hour * 3600 + c.tm_min * 60 + c.tm_sec
    lt = l.tm_hour * 3600 + l.tm_min * 60 + l.tm_sec
    rt = r.tm_hour * 3600 + r.tm_min * 60 + r.tm_sec
    if scheduletype == 0:
        if ltime <= ctime <= rtime:
            return True
    elif scheduletype == 1:
        if lt <= ct <= rt:
            return True
    elif scheduletype == 2:
        if lt <= ct <= rt and c.tm_wday == l.tm_wday:
            return True
    elif scheduletype == 3:
        if lt <= ct <= rt and c.tm_mday == l.tm_mday:
            return True
    elif scheduletype == 4:
        if lt <= ct <= rt and c.tm_mday == l.tm_mday and c.tm_mon == l.tm_mon:
            return True
    return False


def show_timeline_func(request, lat, lng, ctime):
    user = login_status(request)
    if user is None:
        user_status = False
        user_username = None
    else:
        user_status = True
        user_username = user.username

    user_lat = lat
    user_lng = lng
    user_time = ctime
    user_state = None
    user_state_text = None
    search = None
    if request.method == 'POST':
        str_search = request.POST.get('search').strip()
        if str_search is not None and str_search != '':
            search = str_search

    if user is not None:
        user_locations = Location.objects.filter(uid_id=user.id).order_by('-ltime')
        if len(user_locations) > 0 and user_locations[0].sid_id is not None:
            user_state = user_locations[0].sid_id
            user_state_text = State.objects.get(sid=user_state).stext

    note_list = []
    if user is None:
        if search is None:
            all_note_list = Note.objects.all().order_by('-createtime')
        else:
            all_note_list = Note.objects.filter(ntext__contains=search).order_by('-createtime')

        for each_note in all_note_list:
            if each_note.visibility != 2:
                continue
            if user_lat is not None and user_lng is not None and great_circle((user_lat, user_lng), (each_note.lat, each_note.lng)).meters > each_note.radius:
                continue
            if not display(user_time, each_note.starttime, each_note.endtime, each_note.scheduletype):
                continue
            note_list.append(each_note)
    else:
        user_filter_list = Filter.objects.filter(uid_id=user.id)
        if len(user_filter_list) == 0:
            if search is None:
                all_note_list = Note.objects.all().order_by('-createtime')
            else:
                all_note_list = Note.objects.filter(ntext__contains=search).order_by('-createtime')
            for each_note in all_note_list:
                if user_lat is not None and user_lng is not None and great_circle((user_lat, user_lng), (each_note.lat, each_note.lng)).meters > each_note.radius:
                    continue
                if not display(user_time, each_note.starttime, each_note.endtime, each_note.scheduletype):
                    continue

                if each_note.visibility == 0 and each_note.uid_id != user.id:  # only creator self
                    continue
                elif each_note.visibility == 1 and each_note.uid_id != user.id:  # friends
                    try:
                        Friend.objects.get(friender_id=user.id, friendee_id=each_note.uid_id, confirmed=True)
                    except Friend.DoesNotExist:
                        try:
                            Friend.objects.get(friender_id=each_note.uid_id, friendee_id=user.id, confirmed=True)
                        except Friend.DoesNotExist:
                            continue

                note_list.append(each_note)
        else:
            # noteList 符合任意一个 user_filter_list
            if search is None:
                all_note_list = Note.objects.all().order_by('-createtime')
            else:
                all_note_list = Note.objects.filter(ntext__contains=search).order_by('-createtime')
            for each_note in all_note_list:
                if user_lat is not None and user_lng is not None and great_circle((user_lat, user_lng), (each_note.lat, each_note.lng)).meters > each_note.radius:
                    continue
                if not display(user_time, each_note.starttime, each_note.endtime, each_note.scheduletype):
                    continue

                from_friend = True
                try:
                    Friend.objects.get(friender_id=user.id, friendee_id=each_note.uid_id, confirmed=True)
                except Friend.DoesNotExist:
                    try:
                        Friend.objects.get(friender_id=each_note.uid_id, friendee_id=user.id, confirmed=True)
                    except Friend.DoesNotExist:
                        from_friend = False

                if each_note.visibility == 0 and each_note.uid_id != user.id:  # only creator self
                    continue
                elif each_note.visibility == 1 and each_note.uid_id != user.id:  # friends
                    if not from_friend:
                        continue

                insert = False
                totally_not_effect = True
                for each_filter in user_filter_list:
                    take_effect = True
                    if user_state is None and each_filter.sid_id is not None:
                        take_effect = False
                    if user_state is not None and each_filter.sid_id is not None and user_state != each_filter.sid_id:
                        take_effect = False
                    if user_lat is not None and user_lng is not None and great_circle((user_lat, user_lng), (each_filter.lat, each_filter.lng)).meters > each_filter.radius:
                        take_effect = False
                    if not display(user_time, each_filter.starttime, each_filter.endtime, 1):
                        take_effect = False

                    if take_effect:
                        totally_not_effect = False
                        if each_filter.onfriend and not from_friend:
                            continue
                        if each_filter.tid_id is not None:
                            try:
                                NoteTag.objects.get(nid_id=each_note.nid, tid_id=each_filter.tid_id)
                            except NoteTag.DoesNotExist:
                                continue
                        if user_lat is not None and user_lng is not None and great_circle((user_lat, user_lng), (each_note.lat, each_note.lng)).meters > each_note.radius:
                            continue
                        if not display(user_time, each_note.starttime, each_note.endtime, each_note.scheduletype):
                            continue
                        insert = True
                        break

                if insert or totally_not_effect:
                    note_list.append(each_note)
    return render(request, "timeline.html", {'noteList': note_list, 'user_status': user_status, 'user_username': user_username, 'user_state_text': user_state_text, 'lat': user_lat, 'lng': user_lng})


def record_position(request, lat, lng, ctime):
    user = login_status(request)
    if user is not None:
        print("record position in database")


def timeline(request):
    user = login_status(request)
    if user is None:
        user_status = False
        user_username = None
    else:
        user_status = True
        user_username = user.username
    return render(request, "timeline_init.html", {'user_status': user_status, 'user_username': user_username})


def timeline_position(request, lat, lng):
    user_lat = float(lat)
    user_lng = float(lng)
    user_time = timezone.now()
    user = login_status(request)
    if user is not None:
        modify_time = False
        if 'modifyTime' in request.session:
            modify_time = request.session['modifyTime']
        modify_location = False
        if 'modifyLocation' in request.session:
            modify_location = request.session['modifyLocation']

        if modify_location:
            user_lat = request.session['lat']
            user_lng = request.session['lng']
        if modify_time:
            user_time = datetime.datetime.strptime(request.session['datetime'], "%Y-%m-%d %H:%M")
    record_position(request, user_lat, user_lng, user_time)
    return show_timeline_func(request, user_lat, user_lng, user_time)


def note(request, note_id):
    user = login_status(request)
    if user is None:
        user_status = False
        user_username = None
    else:
        user_status = True
        user_username = user.username

    singleNote = Note.objects.get(nid=note_id)
    comments = Comment.objects.filter(nid_id=note_id).order_by('-createtime')
    return render(request, "singleNote.html", {'note': singleNote, 'comments': comments, 'user_status': user_status, 'user_username': user_username})


def submit_comment(request, note_id):
    print("nid is:", note_id)
    user = login_status(request)
    if user is None:
        return HttpResponseRedirect('/account/login/')
    if request.method == 'POST':
        commentString = request.POST.get('comment')
        commentString.strip()
        if commentString == "" or commentString is None:
            return HttpResponse("You did't say anything. . . ")
        else:
            commentObject = Comment(ctext=commentString, nid_id=note_id, uid_id=user.id, createtime=timezone.now())
            commentObject.save()
            return HttpResponseRedirect('/note/' + str(note_id) + '/')
            # return HttpResponse('Your comment is submitted')
    return HttpResponse('sorry, encountered error.')


def filter_list(request):
    user = login_status(request)
    if user is None:
        return HttpResponseRedirect('/account/login/')
    if request.method == 'GET':
        user_filter_list = Filter.objects.filter(uid_id=user.id)
        for each_filter in user_filter_list:
            start_timestamp = each_filter.starttime.timestamp() + 5 * 60 * 60
            end_timestamp = each_filter.endtime.timestamp() + 5 * 60 * 60
            start_datetime = datetime.datetime.fromtimestamp(start_timestamp)
            end_datetime = datetime.datetime.fromtimestamp(end_timestamp)
            each_filter.start_time = start_datetime.strftime("%H:%M")
            each_filter.end_time = end_datetime.strftime("%H:%M")
    if request.method == 'POST':
        delete_filter_id = list(request.POST.keys())[list(request.POST.values()).index('Delete')]
        try:
            delete_filter = Filter.objects.get(fid=delete_filter_id)
        except Filter.DoesNotExist:
            return HttpResponse("Filter does not exist", status=403)
        else:
            if delete_filter.uid_id != user.id:
                return HttpResponse("You cannot modify other's filter", status=403)
            delete_filter.delete()
        return HttpResponseRedirect('/filter/list/')
    return render(request, 'filter_list.html', {'user_filter_list': user_filter_list})


def filter_create(request):
    user = login_status(request)
    if user is None:
        return HttpResponseRedirect('/account/login/')
    lat = 0
    lng = 0
    radius = 0
    starttime = 0
    endtime = 0
    onfriend = 0
    tid_id = None  # tag
    sid_id = None  # state
    uid_id = user.id  # user
    state_list = None  # user state list
    if request.method == 'GET':
        state_list = State.objects.filter(uid=user.id)
    if request.method == 'POST':
        lat = request.POST.get('displayLat')
        lng = request.POST.get('displayLog')
        if (not is_float(lat)) or (not is_float(lng)):
            return HttpResponse("The location is not correct, please select on map and re-try :) ", status=403)
        radius = request.POST.get('radius')
        if not is_float(radius):
            return HttpResponse("The radius you give I cannot understand, would you try another one?", status=403)

        starttime = request.POST.get('startTime')
        endtime = request.POST.get('endTime')
        current_date = timezone.now().strftime("%Y-%m-%d")
        starttime = datetime.datetime.strptime(current_date + ' ' + starttime, "%Y-%m-%d %H:%M")
        endtime = datetime.datetime.strptime(current_date + ' ' + endtime, "%Y-%m-%d %H:%M")
        starttime = datetime.datetime.fromtimestamp(starttime.timestamp() - 5 * 60 * 60)
        endtime = datetime.datetime.fromtimestamp(endtime.timestamp() - 5 * 60 * 60)

        onfriend = int(request.POST.get('onfriend'))
        if onfriend != 0 and onfriend != 1:
            return HttpResponse('Not valid onfriend value', status=403)

        state = int(request.POST.get('state'))
        if state == 0:
            sid_id = None
        else:
            try:
                state_id = State.objects.get(sid=state)
            except State.DoesNotExist:
                return HttpResponse('Not valid state id', status=403)
            else:
                sid_id = state

        tag_name = request.POST.get('tag')
        if tag_name == '':
            tid_id = None
        else:
            try:
                tag = Tag.objects.get(ttext=tag_name)
            except Tag.DoesNotExist:
                tag = Tag(ttext=tag_name)
                tag.save()
                tid_id = tag.tid
            else:
                tid_id = tag.tid
        new_filter = Filter(
            lat=lat,
            lng=lng,
            radius=radius,
            starttime=starttime,
            endtime=endtime,
            onfriend=onfriend,
            tid_id=tid_id,
            sid_id=sid_id,
            uid_id=uid_id
        )
        new_filter.save()
        return HttpResponseRedirect('/filter/list/')
    return render(request, 'filter_create.html', {
        'lat': lat,
        'lng': lng,
        'radius': radius,
        'starttime': starttime,
        'endtime': endtime,
        'onfriend': onfriend,
        'tid_id': tid_id,
        'sid_id': sid_id,
        'uid_id': uid_id,
        'state_list': state_list
    })


def update_state(request):
    user = login_status(request)
    if request.method == "POST":
        sid = request.POST.get('existingStates')
        lat = request.POST.get('displayLat')
        lng = request.POST.get('displayLog')
        if not sid:
            return HttpResponse("You didn't change state!")
        if not sid.isdigit():
            new_state_text = request.POST.get('newState')
            new_state = State(uid=user, stext=new_state_text)
            new_state.save()
            sid = new_state.sid
        else:
            print(sid)
        record = Location(uid=user, ltime=timezone.now(), lat=lat, lng=lng, sid_id=sid, operation="update state")
        record.save()
    return HttpResponseRedirect("/account/profile/")


def backdoor(request):
    user = login_status(request)
    if user is None:
        return HttpResponseRedirect('/account/login/')
    else:
        if 'modifyTime' not in request.session:
            request.session['modifyTime'] = False
        modify_time = request.session['modifyTime']

        if 'modifyLocation' not in request.session:
            request.session['modifyLocation'] = False
        modify_location = request.session['modifyLocation']

        all_notes = Note.objects.all().order_by('-createtime')
        for each_note in all_notes:
            start_timestamp = each_note.starttime.timestamp() + 5 * 60 * 60
            end_timestamp = each_note.endtime.timestamp() + 5 * 60 * 60
            start_datetime = datetime.datetime.fromtimestamp(start_timestamp)
            end_datetime = datetime.datetime.fromtimestamp(end_timestamp)
            each_note.time_date = start_datetime.strftime("%Y-%m-%d")
            each_note.start_time = start_datetime.strftime("%H:%M:%S")
            each_note.end_time = end_datetime.strftime("%H:%M:%S")

        return render(request, 'backdoor.html', {'notes': all_notes, 'modify_time': modify_time, 'modify_location': modify_location})


def backdoor_update(request):
    user = login_status(request)
    if user is None:
        return HttpResponseRedirect('/account/login/')
    else:
        if request.method == "POST":
            modify_time = request.POST.get('modifyTime')
            modify_location = request.POST.get('modifyLocation')
            lat = request.POST.get('displayLat')
            lng = request.POST.get('displayLog')
            sday = request.POST.get('date')
            stime = request.POST.get('time')
            str_date_time = sday + ' ' + stime

            if modify_time == 'True':
                request.session['modifyTime'] = True
            else:
                request.session['modifyTime'] = False

            if modify_location == 'True':
                request.session['modifyLocation'] = True
            else:
                request.session['modifyLocation'] = False

            request.session['lat'] = float(lat)
            request.session['lng'] = float(lng)
            request.session['datetime'] = str_date_time
        return HttpResponseRedirect('/backdoor/')

