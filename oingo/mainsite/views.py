from django.shortcuts import render, HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("index")



def register(request):
    return HttpResponse("register")



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



