from django.db import models
from django.utils.html import format_html


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Author(BaseModel):
    name = models.CharField(max_length=55, unique=True, verbose_name='Author Name')

    def __str__(self):
        return self.name


class Category(BaseModel):
    title = models.CharField(max_length=55, verbose_name='Category title')

    def __str__(self):
        return self.title


class KeyWordSearched(BaseModel):
    keyword = models.CharField(max_length=100, verbose_name='Keyword Searched')

    def __str__(self):
        return self.keyword


class Article(BaseModel):
    title = models.CharField(max_length=150, unique=True)
    summary = models.TextField()
    author = models.ManyToManyField(
        Author,
        related_name='author',
        verbose_name='Author',
    )
    category = models.ForeignKey(
        Category,
        related_name='category',
        verbose_name='Category',
        on_delete=models.PROTECT,
    )
    content = models.TextField()
    article_created_at = models.DateTimeField()
    image_path = models.FilePathField()

    def __str__(self):
        return self.title

    def image_html_tag(self):
        image_tag = format_html("")
        if self.image_path:
            image_tag = format_html(
                '<a href={} target="_blank"><img src="{}" alt="{}" height={} width={}/></a>'.format(
                    self.image_path,
                    self.image_path,
                    self.title,
                    64,
                    64,
                ), )
        return image_tag


class DailySearchResult(BaseModel):
    category = models.ForeignKey(
        Category,
        related_name='categories',
        verbose_name='Category',
        on_delete=models.PROTECT,
    )
    article = models.ForeignKey(
        Article,
        related_name='article',
        verbose_name='Article',
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return self.article


class UserSearchResult(BaseModel):
    keyword = models.ForeignKey(
        KeyWordSearched,
        related_name='keywords',
        verbose_name='Keyword',
        on_delete=models.PROTECT,
    )
    article = models.ForeignKey(
        Article,
        related_name='user_search_result',
        verbose_name='Article',
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return self.article
