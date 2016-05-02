from petshop.settings import *

EMAIL_HOST='localhost'
EMAIL_PORT=1025
DEFAULT_FROM_EMAIL = 'localhost'

CMS_CACHE_DURATIONS = {
    'content': 30,
    'menus': 30,
    'permissions': 0
}

'''
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }
}
'''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '',
        'NAME': 'petshop',
        'USER': 'mi6gan',
        'PASSWORD': ''
    }
}

'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
'''

if DEBUG:
    INSTALLED_APPS += [
        #    'debug_toolbar'
    ]
