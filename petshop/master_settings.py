from petshop.settings import *

DATABASES = {

    'default': {
            'HOST': 'postgres_prod',
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'petshop',
            'USER': 'petshop',
            'PASSWORD': 'qweasd123'
        }
}

DEFAULT_FROM_EMAIL='info@mi6gan.space'
SERVER_EMAIL='info@mi6gan.space'

ADMINS = (('Michael Boyarov',"mi6gan@mail.ru"),)
MANAGERS = (('Michael Boyarov',"mi6gan@mail.ru"),)

ALLOWED_HOSTS = ['pets.mi6gan.space', 'pet-zakupki.ru']

DEBUG = False

EMAIL_SUBJECT_PREFIX = '[pet-zakupki.ru] '

DEFAULT_FROM_EMAIL = 'noreply@mi6gan.space' 
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL
EMAIL_HOST_PASSWORD = 'laer4lazi7Ae'
EMAIL_USE_TLS = True

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'petshop', 'static', 'build'),
)
