from django.contrib.gis.feeds import Feed
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Article
from django.urls import reverse, reverse_lazy

class ArticleListView(ListView):
    template_name = 'blogapp/article_list.html'
    context_object_name = "object_list"
    queryset = (Article.objects.defer("content").
                select_related("author", "category").
                prefetch_related("tags").
                order_by('-pub_date')
                )

class ArticleDetailView(DetailView):
    model = Article

class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return (Article.objects.defer("content").
                select_related("author", "category").
                prefetch_related("tags").
                order_by('-pub_date')[:5]
                )
    def item_title(self, item: Article):
        return item.title
    def item_description(self, item: Article):
        return item.content[:200]
