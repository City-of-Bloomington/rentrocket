from django.conf.urls import patterns, url

from content import views

urlpatterns = patterns(
    '', 
    url(r'blob/(?P<key>.+)$', views.blob),
    url(r'^$', views.home, name='alt_home')
)
