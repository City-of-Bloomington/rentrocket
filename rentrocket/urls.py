from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


#first argument to patterns tells the prefix for the module callback parameter
#here we use '' to keep things generic
urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'allauth.account.views.login', name='login'),
    url(r'^login', 'allauth.account.views.login', name='login'),
    url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
                           
    url(r'^accounts/', include('allauth.urls')),
    url(r'^building/', include('building.urls')),
    url(r'^utility/', include('utility.urls')),
    url(r'^city/', include('city.urls')),


    url(r'^content/', include('content.urls')),

    url(r'^simple-thankyou/$', 'content.views.thankyou'),
    url(r'^simple-thankyou$', 'content.views.thankyou', name='simple-thankyou'),
    url(r'^thankyou/$', 'content.views.thankyou'),
    url(r'^thankyou$', 'content.views.thankyou', name='thankyou'),
    url(r'^share/$', 'content.views.share_data'),
    url(r'^share$', 'content.views.share_data', name='share'),


    url(r'^about$', 'content.views.about', name='about'),
    url(r'^crowdsourcing$', 'content.views.crowdsourcing', name='crowdsourcing'),
    url(r'^partners$', 'content.views.partners', name='partners'),
    url(r'^contact$', 'content.views.contact', name='contact'),
    url(r'^privacy$', 'content.views.privacy', name='privacy'),
    url(r'^terms$', 'content.views.terms', name='terms'),

    url(r'^faq$', 'content.views.faq', name='faq'),
    url(r'^information$', 'content.views.information', name='information'),


    url(r'^welcome$', 'content.views.welcome', name='welcome'),
    url(r'^twitter$', 'content.views.welcome', name='twitter'),
    url(r'^facebook$', 'content.views.welcome', name='facebook'),
    url(r'^gplus$', 'content.views.welcome', name='gplus'),
    
    url(r'^$', 'content.views.welcome', name='welcome'),
)


#only serve static files in development
#in production, they should be served by production server
#https://docs.djangoproject.com/en/1.2/howto/static-files/
## if settings.DEBUG:
##     urlpatterns += patterns('',
##         (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.LOCAL_ROOT + '/static/js'}),
##         (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.LOCAL_ROOT + '/static/css'}),
##         (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.LOCAL_ROOT + '/static/images'}),
##         (r'^favicon.png$', 'django.views.static.serve', {'document_root': settings.LOCAL_ROOT + '/static/images/', 'path': 'favicon.png'}),
##         (r'^apple-touch-icon.png$', 'django.views.static.serve', {'document_root': settings.LOCAL_ROOT + '/static/images/', 'path': 'apple-touch-icon.png'}),
##     )

