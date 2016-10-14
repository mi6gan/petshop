# -*- coding: utf-8 -*-
import os
from django.utils.translation import ugettext_lazy as gettext
DATA_DIR = os.path.dirname(os.path.dirname(__file__))

from oscar.defaults import *

"""
Django settings for petshop project.

Generated by 'django-admin startproject' using Django 1.8.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

ALLOWED_HOSTS = ['pets.mi6gan.space', 'pet-zakupki.ru']
INTERNAL_IPS = ['127.0.0.1']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*10-%4-&2yyv52st%jm19=60yk&fztk3%9%8gi_uag8+#2(@w6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

from oscar import get_core_apps

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.auth',
    'djangocms_text_ckeditor',
    'petshop.sitemaps',
    'cms',
    'menus',
    'sekizai',
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.messages',
    'reversion',
    'easy_thumbnails',
    'filer',
    'cmsplugin_filer_image',
    'cmsplugin_filer_link',
    'cmsplugin_bootstrap_columns',
    'cmsplugin_plaintext',
    'phonenumber_field',
    'ajax_helpers',
    'djangocms_feedback',
    'compressor',
    'widget_tweaks',
    'petshop',
] + get_core_apps([
    'petshop.catalogue',
    'petshop.checkout',
    'petshop.customer',
    'petshop.payment',
    'petshop.shipping',
    'petshop.order',
    'petshop.address',
    'petshop.basket',
    'petshop.partner',
    'petshop.dashboard.communications',
    'petshop.dashboard.catalogue'
])

MIDDLEWARE_CLASSES = (
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'petshop.sitemaps.middleware.SitemapNodeMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware'
)

ROOT_URLCONF = 'petshop.urls'

from oscar import OSCAR_MAIN_TEMPLATE_DIR

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            OSCAR_MAIN_TEMPLATE_DIR
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.template.context_processors.static',

                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',

                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
            ],
        'debug': True,
        'loaders': [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
            'django.template.loaders.eggs.Loader'
        ]},
    },
]

WSGI_APPLICATION = 'petshop.wsgi.application'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'conf', 'locale'),
)

ADMINS = (('Michael Boyarov',"mi6gan@mail.ru"),)

DEFAULT_FROM_EMAIL = 'noreply@mi6gan.space' 


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
STATIC_ROOT = os.path.join(DATA_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'petshop', 'static', 'build'),
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
]

# Common custom settings

SITE_ID = 1

# Oscar custom settings

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'oscar.apps.customer.auth_backends.EmailBackend',
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

DEFAULT_PARTNER = {
    'name': gettext('Primary partner'),
    'code': 'primary'
}

DEFAULT_PRODUCT_CLASS = {
    'name': gettext('Pet product'),
    'slug': 'pet-product'
}

OSCAR_EAGER_ALERTS = False
OSCAR_CURRENCY_FORMAT = u"# руб."
OSCAR_DEFAULT_CURRENCY = "RUR"
OSCAR_EAGER_ALERTS = False
OSCAR_ALLOW_ANON_CHECKOUT = True
OSCAR_PRODUCTS_PER_PAGE = 18
OSCAR_INITIAL_ORDER_STATUS = 'pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'pending': ('checked', 'paid', 'failed'),
    'checked': ('paid', 'failed'),
    'paid': (),
    'failed': ('pending',)
}

LOGIN_REDIRECT_URL = 'customer:profile-view'
OSCAR_ACCOUNTS_REDIRECT_URL = LOGIN_REDIRECT_URL

from django.core.urlresolvers import reverse_lazy
OSCAR_HOMEPAGE = reverse_lazy('pages-root')

# CMS custom settings

CMS_TEMPLATES = (
        ('simple.html', gettext('Simple page')),
        ('main.html', gettext('Main page')),
)
LANGUAGES = (
    ('ru', gettext('Russian')),
)

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'easy_thumbnails.processors.scale_and_crop',
    'easy_thumbnails.processors.filters',
    'easy_thumbnails.processors.background',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location'
)

THUMBNAIL_ALIASES = {
    '': {
        'product_tiny': {
            'size': (48, 48),
            'background': (255, 255, 255)
        },
        'product_small': {
            'size': (125, 125),
            'background': (255, 255, 255)
        },
        'product_medium': {
            'size': (250, 250),
            'background': (255, 255, 255)
        },
        'product_large': {
            'size': (250, 400),
            'background': (255, 255, 255, 255)
        },
        'dashboard_image_input': {
            'size': (200, 200),
            'background': (255, 255, 255)
        }
    },
    'petshop.SiteSettings.logo': {
        'thumb': {
            'size': (0, 96),
            'PRESERVER_EXTENSIONS': ('png',),
        },
    },
    'petshop.SiteSettings.favicon': {
        'thumb': {
            'size': (32, 32)
        }
    }
}

from django.utils.translation import ugettext_lazy as _

OSCAR_DASHBOARD_NAVIGATION = [{
    'label': _('Shop'),
    'icon': 'icon-th-list',
    'children': [
    {
        'label': _('Dashboard'),
        'icon': 'icon-th-list',
        'url_name': 'dashboard:index',
    },
    {
        'label': _('Catalogue'),
        'icon': 'icon-sitemap',
        'children': [{
            'label': _('Products'),
            'url_name': 'dashboard:catalogue-product-list',
        },
        {
            'label': _('Categories'),
            'url_name': 'dashboard:catalogue-category-list',
        }]
    },
    {
        'label': _('Fulfilment'),
        'icon': 'icon-shopping-cart',
        'children': [{
            'label': _('Orders'),
            'url_name': 'dashboard:order-list',
        },
        {
            'label': _('Statistics'),
            'url_name': 'dashboard:order-stats',
        },
        {
            'label': _('Partners'),
            'url_name': 'dashboard:partner-list',
        },
        {
            'label': _('Email templates'),
            'url_name': 'dashboard:comms-list',
        },
        ],
    },
    {
        'label': _('Customers'),
        'icon': 'icon-group',
        'url_name': 'dashboard:users-index'
    },
    ]
}]

FILER_LINK_STYLES = (
    (" ", _("Default")),
    ("btn btn-primary", _("Button")),
)

DJANGOCMS_FEEDBACK_TYPES = [
    {
        'label': gettext('Generic feedback form'),
        'slug': 'feedback',
        'form_class': 'petshop.forms.FeedbackForm'
    },
]

APPEND_SLASH = False

try:
    from protected_settings import *
except ImportError: 
    from protected_settings_sample import *

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE_CLASSES += 'debug_toolbar.middleware.DebugToolbarMiddleware',
