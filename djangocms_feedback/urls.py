from django.conf.urls import patterns, include, url
from . import FeedbackFormsManager

urlpatterns = patterns('',
) + [
    url(r'^%s/' % ft.slug,
	ft.view_class.as_view(form_class=ft.form_class, form_slug=ft.slug),
	name=ft.slug
    ) for ft in FeedbackFormsManager.objects()
]
