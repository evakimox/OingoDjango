from django import forms

from django.core.validators import RegexValidator

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class RegisterForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

