from django.contrib.sitemaps import Sitemap

from .models import Product

class ShopSitemap(Sitemap):
    changefreq='always'
    priority = 0.5
    def items(self):
        return Product.objects.all()[:5]
    def lastmod(self, obj: Product):
        return obj.pk