from django.conf.urls import url

from oscar.core.loading import get_class

from .views import ProductCategoryView, ProductDetailView

urlpatterns = [
    url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)_(?P<pk>\d+)/$', ProductCategoryView.as_view(), name='category'),
    url(r'^(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$', ProductDetailView.as_view(), name='detail')
]
