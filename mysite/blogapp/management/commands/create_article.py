from django.core.management import BaseCommand
from django.db import transaction
from blogapp.models import Author, Tag, Article, Category

class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        author = Author.objects.get(id=2)
        category = Category.objects.get(id=1)
        tags = Tag.objects.filter(name__contains="science").only("id").all()

        article, created = Article.objects.get_or_create(
            title="Hard to Be a God",
            content="is a 1964 science fiction novel by the Soviet writers Arkady and Boris Strugatsky, set in the Noon Universe.",
            author=author,
            category=category,
        )
        for tag in tags:
            article.tags.add(tag)