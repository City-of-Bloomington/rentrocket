from django.conf.urls import patterns, url

from listing import views

urlpatterns = patterns(
    '',

    url(r'new/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)/$', views.new),
    url(r'new/(?P<city_tag>\w+)/(?P<bldg_tag>\w+)/(?P<unit_tag>[\w\%\#]+)$', views.new),

    url(r'new/$', views.new, name='new_listing'),
    url(r'new$', views.new),

    url(r'^$', views.index, name='listing_index'),
)

