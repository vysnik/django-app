from django.contrib.sitemaps import Sitemap

from .models import Article

class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5
    def items(self):
        return Article.objects.order_by("-pub_date")

    def lastmode(self, obj: Article):
        return obj.pk