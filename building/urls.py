from django.conf.urls import patterns, url

from building import views

urlpatterns = patterns('',
    url(r'^in/(?P<lat1>\d+\.\d+)/(?P<lng1>\d+\.\d+)/and/(?P<lat2>\d+\.\d+)/(?P<lng2>\d+\.\d+)/(?P<type>\w+)/(?P<limit>\d+)$', views.lookup, name='search'),
    url(r'^at/(?P<lat>\d+\.\d+)/(?P<lng>\d+\.\d+)/(?P<zoom>\d+)$', views.map, name='map'),
    url(r'^$', views.index, name='index')
)
