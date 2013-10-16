from django.conf.urls import patterns, url

from city import views

urlpatterns = patterns(
    '',
    url(r'resources/(?P<city_tag>\w+)$', views.resources),
    url(r'change/(?P<city_tag>\w+)$', views.change),
    url(r'change$', views.change, name='change_city'),
    url(r'new/$', views.new_city),
    url(r'new$', views.new_city, name='new_city'),
    #url(r'^$', views.index, name='index')
    url(r'^$', views.city, name='city_detail')
)
