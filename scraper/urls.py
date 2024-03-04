from django.urls import path

from .views import scrape_form


app_name = 'scraper'
urlpatterns = [
    path('scrape_form/', scrape_form, name='scrap_form'),
]