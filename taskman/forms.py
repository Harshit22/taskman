from django import forms
#from django.contrib.admin import widgets
from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker', 'placeholder': '01 Jan 2016'})

        
class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=200)
    password = forms.CharField(label='Password', max_length=200,widget=forms.PasswordInput)


class SignUpForm(forms.Form):
    username = forms.CharField(label='Username*', max_length=200)
    fname = forms.CharField(label='First name', max_length=200, required=False)
    lname = forms.CharField(label='Last name', max_length=200, required=False)
    email = forms.EmailField(label='E-mail*', max_length=200)
    password = forms.CharField(label='Password*', max_length=200,widget=forms.PasswordInput)


class AddTaskFrom(forms.Form):
    title = forms.CharField(label='Title', max_length=200)
    comments = forms.CharField(label='Comments', widget=forms.Textarea, required=False)
    deadline = forms.DateField(label='Deadline',widget=DateInput())
