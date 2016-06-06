from django.db.models import Q

from oscar.apps.dashboard.catalogue.views import ProductListView as OscarProductListView
from oscar.core.loading import get_model


class ProductListView(OscarProductListView):

    def apply_search(self, queryset):
        queryset = super(ProductListView, self).apply_search(queryset)
        if not self.form.is_valid():
            return queryset
        data = self.form.cleaned_data
        partner = data.get('partner')
        srecords = get_model('partner', 'StockRecord').objects.all()
        if partner:
            srecords = srecords.filter(partner=partner)
        partner_sku = data.get('partner_sku')
        if partner_sku:
            srecords = srecords.filter(partner_sku__icontains=partner_sku)
        if partner or partner_sku:
            product_pks = srecords.values('product')
            queryset = queryset.filter(
                    Q(pk__in=product_pks)|Q(children__pk__in=product_pks))
        has_image = data.get('has_image')
        if has_image:
            product_pks = get_model(
                    'catalogue', 'ProductImage').objects.values(
                            'product').distinct()
            q0 = Q(pk__in=product_pks)
            q1 = Q(children__pk__in=product_pks)
            if has_image == '1':
                queryset = queryset.filter(q0|q1)
            elif has_image == '2':
                queryset = queryset.exclude(q0).exclude(q1)
        return queryset
