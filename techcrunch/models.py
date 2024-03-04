from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=55, unique=True, verbose_name='Author Name')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    title = models.CharField(max_length=55, verbose_name='Category title')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class KeyWordSearched(models.Model):
    keyword = models.CharField(max_length=100, verbose_name='Keyword Searched')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword


class Article(models.Model):
    title = models.CharField(max_length=150)
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DailySearchResult(models.Model):
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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article


class UserSearchResult(models.Model):
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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article
