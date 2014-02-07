# Django settings for rentrocket project.
import os

# Set up relative references with "os"
BASE_DIR = os.path.abspath(os.path.dirname(__file__)) + os.sep

# Make sure the project is on the PYTHONPATH
import sys
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

ADMINS = (
    ('Admin', 'admin@rentrocket.org'),
)

MANAGERS = ADMINS

#STATIC_ROOT = 'static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

#FORCE_PROD_DB = True

#SETTINGS_MODE='prod' ./manage.py syncdb
#https://developers.google.com/appengine/docs/python/cloud-sql/django
if (os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine')):
    #or
    #FORCE_PROD_DB):
    # Running on production App Engine, so use a Google Cloud SQL database.
    DEBUG = False
    TEMPLATE_DEBUG = DEBUG

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '/cloudsql/rent-rocket:rent-rocket-db',
            'NAME': 'rentrocket',
            'USER': 'root',
        }
    }

    # Absolute path to the directory static files should be collected to.
    # Don't put anything in this directory yourself; store your static files
    # in apps' "static/" subdirectories and in STATICFILES_DIRS.
    # Example: "/var/www/example.com/static/"
    STATIC_ROOT = BASE_DIR + '..' + os.sep + 'static'

    # https://docs.djangoproject.com/en/dev/topics/email/
    #https://bitbucket.org/andialbrecht/appengine_emailbackends/overview
    EMAIL_BACKEND = 'appengine_emailbackend.EmailBackend'

    #this needs to be the same as the one in the database:
    SITE_ID = 2

elif os.getenv('SETTINGS_MODE') == 'prod':
    # Running in development, but want to access the Google Cloud SQL instance
    # in production.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '173.194.111.70',
            'NAME': 'rentrocket',
            'USER': 'root',
            #must add password in manually: (do not commit)
            'PASSWORD': '',            
        }
    }

else:
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

    DATABASES = {
        'default': {
            #sqlite3 only works when running with manage.py
            #will not work when running under app engine:
            #'ENGINE': 'django.db.backends.sqlite3',
            #'NAME': '../rentrocket_db.sq3',

            # Running in development, so use a local MySQL database.
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'rentrocket',
            'USER': 'rentrocket',
            'PASSWORD': 'greenrentals',
            #'HOST': 'localhost',
        }
    }

    # Absolute path to the directory static files should be collected to.
    # Don't put anything in this directory yourself; store your static files
    # in apps' "static/" subdirectories and in STATICFILES_DIRS.
    # Example: "/var/www/example.com/static/"
    STATIC_ROOT = BASE_DIR + '..' + os.sep + 'static' + os.sep + 'auto'

    # Additional locations of static files
    STATICFILES_DIRS = (
        # Put strings here, like "/home/html/static" or "C:/www/django/static".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        #BASE_DIR + 'static',
        BASE_DIR + '..' + os.sep + 'static',
    )

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    #this needs to be the same as the one in the database:
    SITE_ID = 2
    #after a database reset, this is the only one available
    #SITE_ID = 1



# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [".rentrocket.org", ]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''



# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6g)id=q6w^b4t1ya0sgk5!y8oo_bsd%s+k^symeds!t(6*-(2u'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rentrocket.urls'

# Python dotted path to the WSGI application used by Django's runserver.
# not needed when using app engine for hosting:
# WSGI_APPLICATION = 'rentrocket.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows. 
    'rentrocket/templates',
    #'registration_email/templates',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
    
)

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_QUERY_EMAIL = True
DEFAULT_FROM_EMAIL = "rentrocket@gmail.com"
# EMAIL_BACKEND configuration moved above


#http://stackoverflow.com/questions/18780729/django-allauth-verifying-email-only-on-non-social-signup
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    'south',

    'building',
    'city',
    'content',
    'inspection',
    'manager',
    'person',
    'utility',
    'source',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include the providers you want to enable:
    #'allauth.socialaccount.providers.angellist',
    #'allauth.socialaccount.providers.bitly',
    #'allauth.socialaccount.providers.dropbox',

#    'allauth.socialaccount.providers.facebook',

    #'allauth.socialaccount.providers.github',

#    'allauth.socialaccount.providers.google',

    #'allauth.socialaccount.providers.instagram',

#    'allauth.socialaccount.providers.linkedin',

    #'allauth.socialaccount.providers.openid',
    #'allauth.socialaccount.providers.persona',
    #'allauth.socialaccount.providers.soundcloud',
    #'allauth.socialaccount.providers.stackexchange',
    #'allauth.socialaccount.providers.twitch',

#    'allauth.socialaccount.providers.twitter',

    #'allauth.socialaccount.providers.vimeo',
    #'allauth.socialaccount.providers.vk',
    #'allauth.socialaccount.providers.weibo',

    
)


#for making file uploads work with Django on Google app engine.
#need the following settings, assembled from:
#https://docs.djangoproject.com/en/dev/topics/http/file-uploads/
#http://stackoverflow.com/questions/16034059/getting-google-app-engine-blob-info-in-django-view
FILE_UPLOAD_HANDLERS = ("content.custom_upload.BlobstoreFileUploadHandler", )

#these are the original (default) settings:
#("django.core.files.uploadhandler.MemoryFileUploadHandler",
# "django.core.files.uploadhandler.TemporaryFileUploadHandler",)



# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
