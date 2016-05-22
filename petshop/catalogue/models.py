from oscar.apps.catalogue.abstract_models import AbstractProduct

from easy_thumbnails.alias import aliases
from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from django.db.models import Q


class Product(AbstractProduct):

    def thumb(self, image, alias_name):
        if image:
            thumb=thumbnail_url(image.original, alias_name)
        else:
            alias = aliases.get(alias_name)
            thumb = ('http://placehold.it/%sx%s' % 
                            (alias.get('size', (32,32))))
        return thumb

    def primary_thumb(self, alias_name):
        if self.images.exists():
            image = self.primary_image()
        else:
            image = None
        return self.thumb(image, alias_name)

    def tiny_thumb(self):
        return self.primary_thumb('product_tiny')

    def small_thumb(self):
        return self.primary_thumb('product_small')

    def medium_thumb(self):
        return self.primary_thumb('product_medium')

    def large_thumb(self):
        return self.primary_thumb('product_large')

    def thumbs(self, alias_name):
        for image in self.get_thumbs_qs():
            yield self.thumb(image, alias_name)

    def get_thumbs_qs(self):
        return ProductImage.objects.filter(
                Q(product=self)|Q(product__parent=self)).distinct()

    def thumbs_count(self, alias_name):
        return self.get_thumbs_qs.count()

    def tiny_thumbs(self):
        return self.thumbs('product_tiny')

    def small_thumbs(self):
        return self.thumbs('product_small')

    def medium_thumbs(self):
        return self.thumbs('product_medium')

    def large_thumbs(self):
        return self.thumbs('product_large')


from oscar.apps.catalogue.models import *  # noqa

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from cms.models import CMSPlugin
from cms.models.fields import PageField
from filer.fields.file import FilerFileField
from filer.utils.compatibility import python_2_unicode_compatible


DEFULT_LINK_STYLES = (
    (" ", "Default"),
)

LINK_STYLES = getattr(settings, "FILER_LINK_STYLES", DEFULT_LINK_STYLES)


@python_2_unicode_compatible
class CatalogueLinkPlugin(CMSPlugin):
    name = models.CharField(_('name'), max_length=255)
    url = models.CharField(_("url"), blank=True, null=True, max_length=255)
    product = models.ForeignKey(
        'Product',
        verbose_name=_("product page"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        'Category',
        verbose_name=_("catalogue category page"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    page_link = PageField(
        verbose_name=_("page"),
        blank=True,
        null=True,
        help_text=_("A link to a page has priority over urls."),
        on_delete=models.SET_NULL,
    )
    mailto = models.EmailField(_("mailto"), blank=True, null=True,
             help_text=_("An email address has priority over both pages and urls"))
    link_style = models.CharField(_("link style"), max_length=255,
                choices=LINK_STYLES, default=LINK_STYLES[0][0])
    new_window = models.BooleanField(_("new window?"), default=False,
                help_text=_("Do you want this link to open a new window?"))
    file = FilerFileField(blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
        qs = Product.objects.all()
        if instance.categories.exists():
            qs = qs.filter(categories__in=instance.categories.all())


DEFULT_PRODUCTS_CAROUSEL_STYLES = (
    ("default", _("Default")),
)
PRODUCTS_CAROUSEL_STYLES = getattr(
        settings, "PRODUCTS_CAROUSEL_STYLES", DEFULT_PRODUCTS_CAROUSEL_STYLES)

PRODUCTS_CAROUSEL_MAX_COUNT = getattr(
        settings, "PRODUCTS_CAROUSEL_MAX_COUNT", 25)


class ProductsCarouselPlugin(CMSPlugin):
    PRODUCTS_CAROUSEL_ORDERBY = (
        ("date_created", _("Bestselling")),
        ("stats__score", _("Recently added")),
    )
    title = models.CharField(_('title'), max_length=255)
    style = models.CharField(
            verbose_name=_("style"),
            max_length=2048, 
            choices=PRODUCTS_CAROUSEL_STYLES,
            default=PRODUCTS_CAROUSEL_STYLES[0][0])
    products = models.ManyToManyField(
            Product, verbose_name=_("exact product list"),
            help_text=_("If you'll add any product here no automatic"
                        " list will be generated"),
            related_name='+',
            blank=True)
    categories = models.ManyToManyField(
            Category, verbose_name=_("categories"), related_name='+',
            blank=True)
    order_by = models.CharField(
            _("order by"),
            max_length=256,
            choices=PRODUCTS_CAROUSEL_ORDERBY,
            blank=True)
    count = models.PositiveIntegerField(('number of products'),
            validators=[
                MinValueValidator(1),
                MaxValueValidator(PRODUCTS_CAROUSEL_MAX_COUNT)
                ])

    def get_products(self):
        if self.products.exists():
            qs = self.products.all()
        else:
            qs = Product.objects.all()
            if self.categories.exists():
                qs = qs.filter(categories__in=self.categories.all())
            if self.order_by:
                qs = qs.order_by(self.order_by)
        return qs[:self.count]

    def copy_relations(self, oldinstance):
        self.products.clear()
        self.products.add(*oldinstance.products.all())
        self.categories.clear()
        self.categories.add(*oldinstance.categories.all())
