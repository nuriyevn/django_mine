from django.conf.urls import url
from . import views
from django.urls import path
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^old$', views.old, name='old'),
    url(r'^test$', views.test, name='test'),
    url(r'^(?P<instance_id>[0-9]+)/$', views.detail, name='detail' ),
    path("simple/", views.simple, name='simple'),

    path("async/", views.async_view),
    path("sync/", views.sync_view),
    path("newindex/",  views.newindex),
    path("smoke_some_meats/", views.smoke_some_meats),
    path("process/", views.process),
    path('refresh/', views.refresh)
    
]
