import os
import re
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import traceback

from celery import shared_task, Celery
from celery.schedules import crontab
from django.conf import settings
from requests.exceptions import ConnectionError, Timeout
from django.core.management import call_command
from bs4 import BeautifulSoup
import requests
from django.utils.dateparse import parse_date

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from techcrunch.models import Author, Article, Category, DailySearchResult, UserSearchResult, KeyWordSearched
# from techcrunch.resources import export_data
from .forms import ScrapForm

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

chrome_options = Options()
chrome_options.add_argument(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

app = Celery('tasks', broker='redis://localhost:6379/0')


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
            keyword_searched = KeyWordSearched.objects.create(keyword=keyword)
            links = search_keyword(keyword, from_page, to_page)
            created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            folder_path = os.path.join(settings.MEDIA_ROOT, str(keyword).replace(' ', '_')
                                       + '_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                                       )
            os.makedirs(folder_path, exist_ok=True)
            scrape_articles(links, created, folder_path, keyword_searched, type_search='user')
        return HttpResponse("Scraping completed successfully!")
    else:
        form = ScrapForm()
    return render(request, 'scrape_form.html', {'form': form})


@shared_task
def start_techcrunch_daily_scrape():
    links = techcrunch_scrape_by_category()
    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    folder_path = os.path.join(settings.MEDIA_ROOT,
                               '_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                               )
    os.makedirs(folder_path, exist_ok=True)
    scrape_articles(links, created, folder_path, keyword_searched='None', type_search='daily')


@app.task
def techcrunch_scrape_by_category():
    categories = [
        'artificial-intelligence', 'apps', 'biotech-health', 'climate', 'commerce', 'cryptocurrency', 'ec-1',
        'enterprise', 'fintech', 'fundraising', 'gadgets', 'gaming', 'government-policy',
        'growth', 'hardware', 'investor-surveys', 'market-analysis', 'media-entertainment',
        'privacy', 'robotics', 'startups', 'transportation', 'venture'
    ]
    article_data = []
    for cat in categories[:1]:
        url = f'https://techcrunch.com/category/{cat}/'  # URL of the TechCrunch Apps page

        # Set up Selenium WebDriver
        driver = webdriver.Chrome(
            options=chrome_options)  # You may need to download chromedriver.exe and specify its path here
        driver.get(url)

        try:
            while True:
                # Wait for the "Load More" button to become clickable
                load_more_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'load-more'))
                )
                print(load_more_button)
                # Click the "Load More" button
                load_more_button.click()
                print(2)
                # Wait for new articles to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'post-block--image'))
                )
                print(3)
                # Get the updated page source
                page_source = driver.page_source
                # print(page_source)
                # Parse the updated page source with BeautifulSoup
                content = BeautifulSoup(page_source, 'html.parser')
                # Find all article blocks
                articles = content.find_all('article', class_='post-block post-block--image post-block--unread')
                # Extract information from each article block
                for article in articles:
                    article_url = article.find('h2', class_='post-block__title').find('a')['href']
                    date = article.find('time', class_='river-byline__full-date-time')['datetime']
                    if {'article_url': article_url, 'article_date': date} not in article_data:
                        article_data.append({'article_category': cat, 'article_url': article_url, 'article_date': date})
                print(article_data)
                # Check if there are no articles
                if not article_data:
                    break

                # Check the date of the last article extracted
                last_article_date = datetime.strptime(article_data[-1]['article_date'], '%Y-%m-%dT%H:%M:%S')
                if last_article_date < datetime(2024, 2, 1):
                    break  # Stop scraping if the date is before 2024-02-01

        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
        finally:
            # Close the browser
            driver.quit()

    return article_data


@app.task
def search_keyword(keyword, from_page, to_page):
    url = f"https://search.techcrunch.com/search;_ylt=AwrEtsmNyuVlbcA1MqKnBWVH;_ylc=X1MDMTE5NzgwMjkxOQRfcgMyBGZ" \
          f"yA3RlY2hjcnVuY2gEZ3ByaWQDWUV0S2o3SXdRQTJGb08wNExpZkpYQQRuX3JzbHQDMARuX3N1Z2cDNwRvcmlnaW4Dc2VhcmNoLnR" \
          f"lY2hjcnVuY2guY29tBHBvcwMwBHBxc3RyAwRwcXN0cmwDMARxc3RybAM0BHF1ZXJ5A2dvbGQEdF9zdG1wAzE3MDk1NTg1NDA-?" \
          f"p={keyword}&fr2=sb-top&fr=techcrunch"

    links_list = []
    for num in range(from_page, to_page):
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            print(url)
            items = soup.find('ul', {'class': 'compArticleList'}).find_all('li')
            print(len(items))
            for item in items:
                link = item.find('a', class_="fz-20 lh-22 fw-b")['href']
                date = item.find('span', class_='pl-15 bl-1-666').text
                print(link)
                if link not in links_list:
                    links_list.append({'article_url': link, 'article_date': date, 'article_category': ''})

            next_url = soup.find('a', {'class': 'next'})['href']

            if next_url:
                url = next_url
            else:
                break
        except Exception as e:
            print(e)

    return links_list


@app.task
def scrape_articles(articles, created, folder_path, keyword_searched, type_search):
    for article in articles[120:130]:
        print(article)
        if type_search == 'daily':
            url = 'https://www.techcrunch.com' + article['article_url']
        else:
            redirect_url = article['article_url']
            url = extract_article_url(redirect_url)
            # Parse the date string into a datetime object
            try:
                parsed_date = datetime.strptime(article['article_date'], "%B %d, %Y")
            except ValueError:
                # If the date string is not in the expected format, try parsing it using dateutil.parser
                parsed_date = parse_date(article['article_date'])
                print(parsed_date)
            if parsed_date is None:
                parsed_date = datetime.now()

            article['article_date'] = parsed_date.strftime("%Y-%m-%d %H:%M")
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('h1', class_='article__title').text.strip()
            print(title, '\n')
            authors = soup.find('div', class_='article__byline').find('a') \
                .text.replace('AND', ',').replace('BY', '').strip().split(',')
            print(f'author: {authors}', '\n')
            summary = soup.find('p', {'id': 'speakable-summary'}).text
            print(f'summary: {summary}')
            article_contents = soup.find('div', class_='article-content').find_all('p')[1:]

            article_content = '\n'.join(
                paragraph.text for paragraph in article_contents if "Image Credits:" not in paragraph.text)
            print(f'article_content: {article_content}', '\n')
            images = [image['src'] for image in
                      soup.find('article', {'class': 'article-container article--post'}).find_all('img')]
            print(images, '\n')
            if article['article_category'] != '':
                article_category = article['article_category']
            else:
                article_category = 'Uncategorized'
            print(article_category)
            article_created_at = article['article_date']
            print(article_created_at)
            # tags = [tag.text.strip() for tag in soup.find('div', class_='article__tags').find_all('li')]
            # print(tags, '\n')

            image_path = download_images(images, folder_path)
            # Fetch or create authors
            authors = [Author.objects.get_or_create(name=name)[0] for name in authors]

            # Check if the category already exists in the database or create a new one
            print(1)
            category, _ = Category.objects.get_or_create(title=article_category)
            print(2, category)
            # Create a new Article instance and save it into the database
            article = Article.objects.create(
                title=title,
                category=category,
                summary=summary,
                article_created_at=article_created_at,
                created_at=created,
                image_path=image_path,
            )
            print(3)
            # Add the author and category to the article
            article.author.add(*authors)
            # article.category = category
            article.save()
            if type_search == 'daily':
                DailySearchResult.objects.create(category=category, article=article)
            else:
                UserSearchResult.objects.create(keyword=keyword_searched, article=article)
            print(f"Article '{title}' saved successfully!")

        except Exception as e:
            print(f"Error fetching data from {url}: {e}")


@app.task
def extract_article_url(redirect_url):
    response = requests.get(redirect_url, allow_redirects=False, headers=headers)
    if response.status_code == 301 or response.status_code == 302:
        # Extract the 'Location' header, which contains the final destination URL
        final_url = response.headers.get('Location')
        if final_url.startswith("https://search.techcrunch.com/click/") or final_url.startswith(
                'https://r.search.yahoo.com/'):
            # If the final URL still contains a redirect from TechCrunch, follow it recursively
            return extract_article_url(final_url)
        else:
            return final_url
    elif response.status_code == 200:
        response_content = response.content
        # Use regular expressions to extract the URL from the JavaScript code
        match = re.search(r'window\.location\.replace\("(.*?)"\);', response_content.decode('utf-8'))

        # Check if a match is found
        if match:
            true_url = match.group(1)
            print("True URL:", true_url)
            return true_url
        else:
            print("No URL found in the response content.")
    else:
        print(f"Failed to extract final article URL from redirect URL: {redirect_url}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.content}")
        return None


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def download_images(self, image_urls, folder_path):
    saved_image_paths = []
    for image_url in image_urls:
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                # Extract the file name from the URL
                for item in ['.jpg', '.png']:
                    if item in image_url:
                        index = image_url.find(item)
                        if index != -1:
                            image_url = image_url[:index + 4]  # Include the ".jpg" extension
                            print(image_url)

                file_name = image_url.split('/')[-1]

                # Define the file path where the image will be saved
                file_path = os.path.join(folder_path, file_name)

                # Save the image to the file path
                with open(file_path, 'wb') as f:
                    f.write(response.content)

                # Append the relative path of the saved image to the list
                saved_image_paths.append(file_path.replace(settings.MEDIA_ROOT, ''))
            else:
                print(f"Failed to download image from {image_url}. Status code: {response.status_code}")
        except (ConnectionError, Timeout) as e:
            # Log the connection timeout error
            print(f"Error downloading image: {e}")
            # Retry the task
            self.retry(exc=e)
        except Exception as e:
            # Log other unexpected errors
            print(f"Unexpected error: {e}")
    if saved_image_paths:
        return saved_image_paths[0]
    else:
        'no_image'
