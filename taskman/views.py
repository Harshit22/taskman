from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login as login_auth, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError 
from .models import Task, Feed
from django.db.models.functions import Lower
from .forms import LoginForm, SignUpForm, AddTaskFrom

# Create your views here.

def login(request):
    if request.method == 'POST':
        if request.POST.get('login', False):
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                login_auth(request, user)
                return HttpResponseRedirect(reverse('taskman:index'))
            else:
                error = "Login failed."
                return render(request, 'taskman/login.html', {'login_error': error, 'loginform' : LoginForm, 'signupform' : SignUpForm})
            
        if request.POST.get('signup', False):
            data = SignUpForm(request.POST)
            try:
                user = User.objects.create_user(username = request.POST['username'],
                                                first_name = request.POST['fname'],
                                                last_name = request.POST['lname'],
                                                email = request.POST['email'],
                                                password = request.POST['password'])                
                user.save()
                user = authenticate(username=request.POST['username'], password=request.POST['password'])
                login_auth(request, user)
                return HttpResponseRedirect(reverse('taskman:index'))
            except IntegrityError:
                error = "Username already taken"
                return render(request, 'taskman/login.html', {'sign_up_error': error, 'loginform' : LoginForm, 'signupform' : SignUpForm})
            except ValueError:
                error = "One of the required fields is blank"
                return render(request, 'taskman/login.html', {'sign_up_error': error, 'loginform' : LoginForm, 'signupform' : SignUpForm})                
  
        if request.POST.get('logout', False):
            logout(request)
        
    return render(request, 'taskman/login.html', {'loginform' : LoginForm, 'signupform' : SignUpForm})


@login_required(redirect_field_name = None, login_url='/taskman/login/')
def index(request):
    user = request.user
    open_order_by = 'deadline'
    closed_order_by = 'title'
    
    if request.method == 'GET':
        type = request.GET.get('type', None)
        if type == 'open':
            open_order_by = request.GET.get('order_by', None)
        elif type == 'closed':
            closed_order_by = request.GET.get('order_by', None)
        
    open_tasks = Task.objects.get_open_tasks(user, open_order_by)
    closed_tasks = Task.objects.get_closed_tasks(user, closed_order_by)
    
    if request.method == 'POST':       
        if 'task_edits' in request.POST:            
            option = request.POST['task_edits']
            task_keys = request.POST.getlist('pk')
            Task.objects.edit_all(option = option, user = user, task_keys = task_keys)          
                
        return HttpResponseRedirect(reverse('taskman:index'))
                
    return render(request, 'taskman/index.html', {'user' : user, 'open_tasks' : open_tasks, 'closed_tasks' :closed_tasks})

    
@login_required(redirect_field_name = None, login_url='/taskman/login/')
def feed(request):
    user = request.user
    feed = user.feed_set.all().order_by('-date') #RF
    context = {'user': user,
               'feed': feed }
    
    return render(request, 'taskman/feed.html', context)


@login_required(redirect_field_name = None, login_url='/taskman/login/')
def add(request):
    user = request.user
    
    if request.method == 'POST':
        try:
            Task.objects.add_task(user, request.POST)
            return HttpResponseRedirect(reverse('taskman:index'))
            
        except ValueError:
            error = 'One of the fields was not properly filled. Try again.'
            return render(request, 'taskman/add.html', {'user' : user, 'addtaskform' : AddTaskFrom, 'add_task_error' :error})
                        
    return render(request, 'taskman/add.html', {'user' : user, 'addtaskform' : AddTaskFrom})


def _404(request):
    return HttpResponseRedirect(reverse('taskman:index'))
