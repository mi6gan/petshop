from django.conf import settings
from django.conf.urls import *  # NOQA
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.core.urlresolvers import reverse_lazy
from django.views import static
from django.views.i18n import javascript_catalog

from oscar.core.loading import get_class
from oscar.views.decorators import login_forbidden

basket_urls = get_class('basket.app', 'application').urls
checkout_urls = get_class('checkout.app', 'application').urls
promotion_urls = get_class('promotions.app', 'application').urls
dashboard_urls = get_class('dashboard.app', 'application').urls
payment_urls = get_class('payment.urls', 'urlpatterns')
petshop_sitemap = get_class('sitemaps.views', 'petshop_sitemap')
password_reset_form = get_class('customer.forms', 'PasswordResetForm')
set_password_form = get_class('customer.forms', 'SetPasswordForm')

urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
        url(r'^sitemap.xml$', petshop_sitemap),
        url(r'^feedback/', include('djangocms_feedback.urls'), name='feedback'),
        url(r'^basket/', include(basket_urls)),
        url(r'^checkout/', include(checkout_urls)),
        url(r'^promotion/', include(promotion_urls)),
        url(r'^dashboard/', include(dashboard_urls)),
        url(r'^payment/', include(payment_urls, 'payment')),
        url(r'^password-reset/$',
                login_forbidden(auth_views.password_reset),
                {'password_reset_form': password_reset_form,
                 'post_reset_redirect': reverse_lazy('password-reset-done')},
                name='password-reset'),
        url(r'^password-reset/done/$',
                login_forbidden(auth_views.password_reset_done),
                name='password-reset-done'),
        url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
                login_forbidden(auth_views.password_reset_confirm),
                {
                    'post_reset_redirect': reverse_lazy('password-reset-complete'),
                    'set_password_form': set_password_form,
                },
                name='password-reset-confirm'),
        url(r'^password-reset/complete/$',
                login_forbidden(auth_views.password_reset_complete),
                name='password-reset-complete'),
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
