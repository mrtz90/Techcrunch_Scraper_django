from django.shortcuts import render

from django.http import HttpResponse

from techcrunch.models import Author, Article, Category, DailySearchResult, UserSearchResult, KeyWordSearched
# from techcrunch.resources import export_data
from .forms import ScrapForm


def scrape_form(request):
    """
    View function to handle the scraping form submission.
    """
    if request.method == 'POST':
        form = ScrapForm(request.POST)
        if form.is_valid():
            key_word = form.cleaned_data['key_word']
            from_page = form.cleaned_data['from_page']
            to_page = form.cleaned_data['to_page']
            export_format = form.cleaned_data['export_format']
            keyword_searched = KeyWordSearched.objects.create(key_word=key_word)

        return HttpResponse("Scraping completed successfully!")
    else:
        form = ScrapForm()
    return render(request, 'scrape_form.html', {'form': form})
