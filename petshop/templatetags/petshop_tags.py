from django import template
from django.forms.widgets import Media

register = template.Library()

@register.simple_tag
def render_base_js():
    media = (
        Media(
            js=(
                'vendor/js/jquery.min.js',
                'vendor/js/move-top.js',
                'vendor/js/easing.js',
                'vendor/js/startstop-slider.js',
            )
        )
    )
    return u'\n'.join(media.render_js())
