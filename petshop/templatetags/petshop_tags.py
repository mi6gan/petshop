from petshop.basket.forms import MiniBasketLineFormSet
   
from django.forms.widgets import Media
from django.template.loader import render_to_string

from django import template

from sekizai.helpers import get_varname

register = template.Library()

@register.assignment_tag
def get_base_media():
    media = (
        Media(
            js=(
                'vendor/js/jquery.min.js',
                'vendor/js/easing.js',
                'vendor/js/move-top.js',
                'vendor/js/bootstrap/alert.js',
                'js/base.js',
            ),
            css={
                'all': (
                    'css/base.css', 'vendor/css/bootstrap.css',
                    'vendor/font-awesome/css/font-awesome.css'
                )
            }
        )
    )
    return media

@register.assignment_tag
def get_dashboard_media():
    media = (
        Media(
            js=(
                'vendor/js/inputmask/inputmask.js',
                'vendor/js/inputmask/jquery.inputmask.js',
                'vendor/js/tinymce/jquery.tinymce.min.js',
                'vendor/js/tinymce/tinymce.min.js',
                'vendor/js/select2/select2.full.min.js',
                'vendor/js/bootstrap/button.js',
                'vendor/js/bootstrap/collapse.js',
                'vendor/js/bootstrap/tab.js',
                'vendor/js/bootstrap/dropdown.js',
                'vendor/oscar/js/ui.js',
                'djangocms_text_ckeditor/ckeditor/ckeditor.js',
                'vendor/oscar/js/dashboard.js',
            ),
            css = {
                'all': {
                    'css/dashboard.css'
                }
            }
        )
    )
    return media

@register.simple_tag(takes_context=True)
def extend_media_block(context, media_type, media, block_name=None):
    if not block_name:
        block_name = media_type
    sekizai_varname = get_varname()
    rendered_content = getattr(media, 'render_%s' % media_type)()
    rendered_content = u'\n'.join([c.strip() for c in rendered_content])
    context[sekizai_varname][block_name].append(rendered_content)
    return ''

@register.simple_tag(takes_context=True)
def render_mini_basket(context):
    request = context.get('request')
    formset = MiniBasketLineFormSet(strategy=request.strategy,
                                    queryset=request.basket.lines.all())
    context.update(dict(basket=request.basket, formset=formset))
    content = render_to_string('basket/mini_basket.html', context)
    return content
