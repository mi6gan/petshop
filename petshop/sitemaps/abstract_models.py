from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from decimal import Decimal as D


class SitemapNode(models.Model):
    ALWAYS = None
    HOURLY = 1
    DAILY = 24
    WEEKLY = 24*7
    MONTHLY = 24*7*30
    YEARLY = 24*7*30*12
    NEVER = 0

    CHANGEFREQ_CHOICES = (
        (ALWAYS, 'always'),
        (HOURLY, 'hourly'),
        (DAILY, 'daily'),
        (WEEKLY, 'weekly'),
        (MONTHLY, 'monthly'),
        (YEARLY, 'yearly'),
        (NEVER, 'never')
    )

    changefreq = models.PositiveIntegerField(
            choices=CHANGEFREQ_CHOICES, null=True, default=None)
    lastmod = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=200)
    priority = models.DecimalField(
            max_digits=2, decimal_places=1, validators=[
                MinValueValidator(D('0.0')), MaxValueValidator(D('1.0'))],
            default=D('0.8'))
    include = models.BooleanField(default=True)

    def get_edit_url(self):
        name = self.__class__.__name__.lower()
        if self.pk:
            return reverse('admin:sitemaps_%s_change' % name, args=[self.pk])
        else:
            return reverse('admin:sitemaps_%s_create' % name)

    @property
    def has_changes(self):
        return False

    @classmethod
    def get(cls, obj):
        if hasattr(obj, 'sitemap_node') and obj.sitemap_node:
            return obj.sitemap_node

    @classmethod
    def get_or_update(cls, obj):
        node = cls.get(obj)
        updated = False
        if node and node.has_changes:
            if (not node.changefreq or 
                    node.lastmod == None or
                    (timezone.now() - node.lastmod).total_seconds > (
                        node.changefreq*60*60)):
                node.lastmod = timezone.now()
                node.save()
                updated = True
        return node, updated

    class Meta:
        abstract = True
        verbose_name = (_('Sitemap options'))
        verbose_name_plural = (_('Sitemap options'))
