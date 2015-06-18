from django.conf.urls import patterns, url

from listing import views

urlpatterns = patterns(
    '',

    url(r'(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)/new/$', views.new),
    url(r'(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)/new$', views.new),
    url(r'(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/new/$', views.new),
    url(r'(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/new$', views.new),

    url(r'(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)/$', views.index),
    url(r'(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)$', views.index),
    url(r'(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/$', views.index),
    url(r'(?P<city_tag>\w+)/(?P<bldg_tag>\w+)$', views.index),

    url(r'new/$', views.new_temp, name='new_listing'),
    url(r'new$', views.new_temp),

    url(r'^$', views.index, name='listing_index'),
)

