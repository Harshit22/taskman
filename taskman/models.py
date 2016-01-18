from django.db import models
from django.contrib.auth.models import User

# Create your models here.

##class User(models.Model):
##    first_name = models.CharField(max_length = 200, blank = False)
##    last_name = models.CharField(max_length = 200, blank = True)
##    email = models.EmailField(max_length = 200, unique = True, blank = False)
##    password = models.CharField(max_length = 200, blank = False)
##    join_date = models.DateTimeField('Joined On', blank = False)
##    def __str__(self):
##        return self.first_name + ' ' +  self.last_name

class Task(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 200, blank = False)
    comments = models.TextField(blank = True)
    added_date = models.DateTimeField('Added On', blank = False)
    deadline = models.DateField('Deadline', blank = False)
    completed = models.BooleanField(default = False)
    def __str__(self):
        return self.title
    def isCompleted(self):
        return self.completed

class Feed(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    message = models.TextField(blank = False)
    date = models.DateTimeField(blank = False)
    def __str__(self):
        return self.message    
    
