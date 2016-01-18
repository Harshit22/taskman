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

a = (lambda l: "s<b>" if l > 1 else "<b>")
b = (lambda i: "'," if i > 1 else "")

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
    
    if request.method == 'POST':
        
        if request.POST['task_edits']:
            
            value = request.POST['task_edits']
            if value == "Mark open":
                task_keys = request.POST.getlist('pk')
                message = "You reopened task" + a(len(task_keys))
                for index, pkey in enumerate(task_keys,start = 1):
                    task = get_object_or_404(Task, pk = pkey)
                    task.completed = False
                    task.save()
                    message += " " + b(index) + "'" + task.title

                message += "'</b>."
                feed = Feed(user = user, message = message, date = timezone.now())
                feed.save()                

            if value == "Mark closed":
                task_keys = request.POST.getlist('pk')
                message = "You closed task" + a(len(task_keys))
                for index, pkey in enumerate(task_keys,start = 1):
                    task = get_object_or_404(Task, pk = pkey)
                    task.completed = True
                    task.save()
                    message += " " + b(index) + "'" + task.title

                message += "'</b>."
                feed = Feed(user = user, message = message, date = timezone.now())
                feed.save()
                
            if value == "Delete":
                task_keys = request.POST.getlist('pk')
                message = "You deleted task" + a(len(task_keys))
                for index, pkey in enumerate(task_keys,start = 1):
                    task = get_object_or_404(Task, pk = pkey)
                    task.delete()
                    message += " " + b(index) + "'" + task.title

                message += "'</b>."
                feed = Feed(user = user, message = message, date = timezone.now())
                feed.save()

            open_tasks = user.task_set.filter(completed = False)
            closed_tasks = user.task_set.filter(completed = True)            
                
        return HttpResponseRedirect(reverse('taskman:index'))

    open_tasks = user.task_set.filter(completed = False).order_by('deadline')
    closed_tasks = user.task_set.filter(completed = True).order_by(Lower('title'))

    if request.method == 'GET':
        t = request.GET.get('type', None)
        s = request.GET.get('order_by', None)
        if t == 'open' and s:
            if s == 'title':
                open_tasks = user.task_set.filter(completed = False).order_by(Lower(s)) #asc
            elif s == 'deadline':
                open_tasks = user.task_set.filter(completed = False).order_by(s)  #asc; approaching deadlines at top
            elif s == 'added_date':
                open_tasks = user.task_set.filter(completed = False).order_by('-' + s)  #desc; recently added at top
                
            
        if t == 'closed' and s:
            if s == 'title':
                closed_tasks = user.task_set.filter(completed = True).order_by(Lower(s)) #asc
            elif s == 'deadline':
                closed_tasks = user.task_set.filter(completed = True).order_by('-' + s)  #desc; recently closed at top
            elif s == 'added_date':
                closed_tasks = user.task_set.filter(completed = True).order_by('-' + s)  #desc; recently added at top
            
            
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
        print(request.POST['deadline']) #RF
        try:
            if request.POST['title'] == '':
                raise ValueError
            task = Task(user = user,
                        title = request.POST['title'],
                        comments = request.POST['comments'],
                        added_date = timezone.now(),
                        deadline = datetime.strptime(request.POST['deadline'], '%d %b %Y').strftime('%Y-%m-%d'))
            task.save()

            message = "You created a task <b>'" + task.title + "'</b>, to be completed by " + task.deadline + "."
            feed = Feed(user = user, message = message, date = timezone.now())
            feed.save()

            return HttpResponseRedirect(reverse('taskman:index'))
            
        except ValueError:
            error = 'One of the fields was not properly filled. Try again.'
            return render(request, 'taskman/add.html', {'user' : user, 'addtaskform' : AddTaskFrom, 'add_task_error' :error})
                        
    return render(request, 'taskman/add.html', {'user' : user, 'addtaskform' : AddTaskFrom})


def _404(request):
    return HttpResponseRedirect(reverse('taskman:index'))
