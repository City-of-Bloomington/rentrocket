from django.conf.urls import patterns, url

from building import views

urlpatterns = patterns(
    '',
    url(r'in/(?P<lat1>\d+\.\d+)/(?P<lng1>\d+\.\d+)/and/(?P<lat2>\d+\.\d+)/(?P<lng2>\d+\.\d+)/(?P<type>\w+)/(?P<limit>\d+)$', views.lookup, name='search'),
    url(r'in/(?P<lat1>[\-\d]+\.\d+)/(?P<lng1>[\-\d]+\.\d+)/and/(?P<lat2>[\-\d]+\.\d+)/(?P<lng2>[\-\d]+\.\d+)$', views.lookup),
    url(r'at/(?P<lat>[\-\d]+\.\d+)/(?P<lng>[\-\d]+\.\d+)/(?P<zoom>\d+)$', views.map, name='map'),
    url(r'(?P<city_tag>\w+)$', views.city_map, name='city_map'),
    #url(r'^$', views.index, name='index')
    url(r'^$', views.map, name='building_index')
)
