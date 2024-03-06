from django.urls import path

from .views import article_report


app_name = 'scraper'
urlpatterns = [
    path('article_report/', article_report, name='article_report'),
]
