from django.conf.urls import patterns, url

from building import views

urlpatterns = patterns(
    '',

    #json result:
    url(r'search/(?P<query>[\w\%\#]+)$', views.search_geo, name='search_geo'),
    url(r'search/$', views.search_geo),
    
    url(r'new/(?P<query>[\w\%\#]+)$', views.new, name='new_building'),
    url(r'new/$', views.new),
    url(r'new$', views.new),

    url(r'in/(?P<city_tag>\w+)/between/(?P<lat1>[\-\d]+\.\d+)/(?P<lng1>[\-\d]+\.\d+)/and/(?P<lat2>[\-\d]+\.\d+)/(?P<lng2>[\-\d]+\.\d+)$', views.lookup),
    url(r'between/(?P<lat1>\d+\.\d+)/(?P<lng1>\d+\.\d+)/and/(?P<lat2>\d+\.\d+)/(?P<lng2>\d+\.\d+)/(?P<type>\w+)/(?P<limit>\d+)$', views.lookup, name='buildings_on_map'),
    url(r'between/(?P<lat1>[\-\d]+\.\d+)/(?P<lng1>[\-\d]+\.\d+)/and/(?P<lat2>[\-\d]+\.\d+)/(?P<lng2>[\-\d]+\.\d+)$', views.lookup),
    url(r'at/(?P<lat>[\-\d]+\.\d+)/(?P<lng>[\-\d]+\.\d+)/(?P<zoom>\d+)$', views.map, name='map'),
    url(r'in/(?P<city_tag>\w+)/matching/(?P<query>\w+)$', views.match_existing),
    url(r'in/(?P<city_tag>\w+)/matching/$', views.match_existing),



    url(r'unit/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)/edit/$', views.unit_edit),
    url(r'unit/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)/edit$', views.unit_edit),
    url(r'unit/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/edit$', views.unit_edit),
    
    url(r'unit/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)/json/$', views.unit_json),
    url(r'unit/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)/json$', views.unit_json),
    url(r'unit/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)/$', views.unit_details, name='unit_details'),
    url(r'unit/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)$', views.unit_details, name='unit_details'),
    url(r'unit/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/$', views.unit_details, name='unit_details'),
    url(r'unit/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)$', views.unit_details, name='unit_details'),
    
    #TODO: reorder the order of bldg_tag and city_tag
    ## url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/update/$', views.update),
    ## url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/update$', views.update),
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/edit/$', views.edit),
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/edit$', views.edit),
    ## url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/json/$', views.send_json),
    ## url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/json$', views.send_json),
    #url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)/$', views.details, name='details),
    url(r'(?P<bldg_tag>\w+)/(?P<city_tag>\w+)$', views.details, name='details'),

    url(r'^$', views.map, name='building_index')
)
