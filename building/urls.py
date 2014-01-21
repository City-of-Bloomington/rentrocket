from django.conf.urls import patterns, url

from building import views

urlpatterns = patterns(
    '',
    url(r'in/(?P<lat1>\d+\.\d+)/(?P<lng1>\d+\.\d+)/and/(?P<lat2>\d+\.\d+)/(?P<lng2>\d+\.\d+)/(?P<type>\w+)/(?P<limit>\d+)$', views.lookup, name='search'),
    url(r'in/(?P<lat1>[\-\d]+\.\d+)/(?P<lng1>[\-\d]+\.\d+)/and/(?P<lat2>[\-\d]+\.\d+)/(?P<lng2>[\-\d]+\.\d+)$', views.lookup),
    url(r'at/(?P<lat>[\-\d]+\.\d+)/(?P<lng>[\-\d]+\.\d+)/(?P<zoom>\d+)$', views.map, name='map'),
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/update/$', views.update),
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/update$', views.update),
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/edit/$', views.edit),
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/edit$', views.edit),
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/json/$', views.send_json),
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/json$', views.send_json),
    #url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/$', views.details, name='details)
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)$', views.details, name='details')
    #url(r'^$', views.index, name='index')
    url(r'^$', views.map, name='building_index')
)
