from django.conf.urls import url

from . import views

app_name = 'taskman'

urlpatterns = [
    # ex: /taskman/login
    url(r'^login/$', views.login, name='login'),    
    # ex: /taskman/
    url(r'^$', views.index, name='index'),
    # ex: /taskman/feed/
    url(r'^feed/$', views.feed, name='feed'),
    # ex: /taskman/add/   
    url(r'^add/$', views.add, name='add'),
    # ex: /taskman/dkalkaejflakhf/sfsfs
    #url(r'', views._404, name='_404'),    
]


