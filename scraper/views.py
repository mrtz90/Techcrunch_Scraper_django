import os
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import logging

from django.conf import settings

from .forms import ScrapForm
from .tasks import scrape_articles, search_keyword


logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}


def scrape_form(request):
    """
    View function to handle the scraping form submission.
    """
    if request.method == 'POST':
        form = ScrapForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['key_word']
            from_page = form.cleaned_data['from_page']
            to_page = form.cleaned_data['to_page']
            export_format = form.cleaned_data['export_format']
            links = search_keyword(keyword, from_page, to_page)
            created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            folder_path = os.path.join(settings.MEDIA_ROOT, str(keyword).replace(' ', '_')
                                       + '_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                                       )
            type_search = 'user'
            os.makedirs(folder_path, exist_ok=True)

            result = scrape_articles.delay(
                links, created, folder_path,
                export_format, type_search, keyword)
            print(result.status)
        return HttpResponse("Scraping completed successfully!")
    else:
        form = ScrapForm()
    return render(request, 'scrape_form.html', {'form': form})
