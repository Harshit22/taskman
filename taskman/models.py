from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone
from django.contrib.auth.models import User

a = (lambda l: "s<b>" if l > 1 else "<b>")
b = (lambda i: "'," if i > 1 else "")

class TaskManager(models.Manager):

    order_by_list = ['title', 'deadline', 'added_date',         #asc
                     '-title', '-deadline', '-added_date']      #desc
    
    def add_task(self, user, POST):
        if POST['title'] == '':
            raise ValueError
        task = Task(user = user,
                    title = POST['title'],
                    comments = POST['comments'],
                    added_date = timezone.now(),
                    deadline = datetime.strptime(POST['deadline'], '%d %b %Y').strftime('%Y-%m-%d'))
        task.save()

        message = "You created a task <b>'" + task.title + "'</b>, to be completed by " + task.deadline + "."
        Feed.objects.add_feed(user = user, message = message, date = timezone.now())        

    def reopen(self, user, task_keys):
        message = "You reopened task" + a(len(task_keys))
        for index, pkey in enumerate(task_keys,start = 1):
            task = get_object_or_404(Task, pk = pkey)
            task.completed = False
            task.save()
            message += " " + b(index) + "'" + task.title

        message += "'</b>."
        Feed.objects.add_feed(user = user, message = message, date = timezone.now())

    def close(self, user, task_keys):
        message = "You closed task" + a(len(task_keys))
        for index, pkey in enumerate(task_keys,start = 1):
            task = get_object_or_404(Task, pk = pkey)
            task.completed = True
            task.save()
            message += " " + b(index) + "'" + task.title

        message += "'</b>."
        Feed.objects.add_feed(user = user, message = message, date = timezone.now())

    def delete(self, user, task_keys):
        message = "You deleted task" + a(len(task_keys))
        for index, pkey in enumerate(task_keys,start = 1):
            task = get_object_or_404(Task, pk = pkey)
            task.delete()
            message += " " + b(index) + "'" + task.title

        message += "'</b>."
        Feed.objects.add_feed(user = user, message = message, date = timezone.now())

    def edit_all(self, option, user, task_keys):
        if option == "Mark open":
            self.reopen(user = user, task_keys = task_keys)
        elif option == "Mark closed":
            self.close(user = user, task_keys = task_keys)
        elif option == "Delete":
            self.delete(user = user, task_keys = task_keys)

    def get_open_tasks(self, user, order_by = 'deadline'):
        if order_by not in self.order_by_list:
            order_by = 'deadline'

        if order_by.find('title') != -1:
            return user.task_set.filter(completed = False).order_by(Lower(order_by))
        else:
            return user.task_set.filter(completed = False).order_by(order_by)

    def get_closed_tasks(self, user, order_by = 'title'):
        if order_by not in self.order_by_list:
            order_by = 'title'
            
        if order_by.find('title') != -1:
            return user.task_set.filter(completed = True).order_by(Lower(order_by))
        else:
            return user.task_set.filter(completed = True).order_by(order_by)    

class FeedManager(models.Manager):
    def add_feed(self, user, message, date):
        feed = Feed(user = user, message = message, date = timezone.now())
        feed.save()

    
class Task(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 200, blank = False)
    comments = models.TextField(blank = True)
    added_date = models.DateTimeField('Added On', blank = False)
    deadline = models.DateField('Deadline', blank = False)
    completed = models.BooleanField(default = False)
    objects = TaskManager()
    def __str__(self):
        return self.title
        

class Feed(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    message = models.TextField(blank = False)
    date = models.DateTimeField(blank = False)
    objects = FeedManager()
    def __str__(self):
        return self.message    
    
