from django.conf import settings
from django.conf.urls import *  # NOQA
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views import static
from django.views.i18n import javascript_catalog

from .catalogue.urls import urlpatterns as catalogue_urls

urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
        url(r'^catalogue/', include(catalogue_urls, 'catalogue')),
        url(r'^jsi18n/$', javascript_catalog, name='javascript_catalog'),
        url(r'^', include('cms.urls'), name='pages-root'),
]

# This is only needed when using runserver.
if settings.DEBUG:
    try:
        import debug_toolbar
        debug_urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] if 'debug_toolbar' in settings.INSTALLED_APPS else []
    except ImportError:
        debug_urlpatterns = []
    debug_urlpatterns += [
        url(r'^media/(?P<path>.*)$', static.serve,
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ] + staticfiles_urlpatterns()
    urlpatterns = debug_urlpatterns + urlpatterns
