from django.contrib import admin

from import_export.admin import ExportMixin

from .models import Author, Article, Category, DailySearchResult, UserSearchResult, KeyWordSearched


@admin.register(Article)
class ArticleAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'id', 'image_html_tag', 'title', 'display_authors', 'summary', 'category',
        'keyword', 'article_created_at', 'image_path'
    ]
    list_display_links = ['id', 'title']
    list_filter = ['title', 'author', 'category']

    @staticmethod
    def display_authors(obj):
        return ", ".join([author.name for author in obj.author.all()])


@admin.register(Author)
class AuthorAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'id', 'name'
    ]


@admin.register(Category)
class CategoryAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'id', 'title'
    ]


@admin.register(KeyWordSearched)
class KeywordSearchedAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'id', 'keyword',
    ]


@admin.register(DailySearchResult)
class DailySearchResultAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'id', 'category', 'created_at'
    ]


@admin.register(UserSearchResult)
class UserSearchedAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'id', 'keyword',
    ]
