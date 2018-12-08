"""oingo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from mainsite import views

urlpatterns = [
    path('admin/', admin.site.urls),


    path('', views.index),
    path('account/register/', views.register),
    path('account/register/success/', views.register_success),
    path('account/login/', views.login),
    path('account/login/success/', views.login_success),
    path('account/logout/', views.logout),
    path('account/profile/', views.account_profile_redirect),
    path('account/profile/<str:profile_username>/', views.account_profile),
    path('account/settings/', views.account_settings),
    path('note/<int:noteid>', views.note),
    path('friend/list/', views.friend_list),
    path('friend/request/', views.friend_request),
    path('note/create', views.create_note),
    path('filter/list/', views.filter_list),
    path('filter/create/', views.filter_create),
    path('filter/settings/<int:fid>/', views.filter_settings),




]
