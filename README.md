# Techcrunch Scraper
## Introduction
Techcrunch Scraper is a Django application designed for scraping articles from the TechCrunch website. It utilizes Celery for task scheduling and execution. This application provides functionality for both manual scraping based on user input and automated daily scraping.

## Prerequisites
Python 3.x
Django
Celery
Redis
Selenium (for automated scraping)
Beautiful Soup (for web scraping)
## Installation
Clone the repository to your local machine.
#### Install the required Python packages using pip:
```dash
pip install -r requirements.txt
```
#### Install and run Redis server. You can download it from Redis website.
#### Configure the Django project settings in config/settings.py.
## Run Django migrations:
```dash
python manage.py migrate
```
## Usage
#### Manual Scraping
#### Access the scraping form at /scrape-form.
#### Enter the keyword, start page, end page, and export format.
#### Submit the form to initiate the scraping process.
#### Automated Daily Scraping
## Start Celery worker:
```dash
celery -A scraper worker --loglevel=info
```
## Start Celery Beat for task scheduling:
```dash
celery -A scraper beat --loglevel=info
```
## Task Definitions
##### scrape_form: View function to handle manual scraping form submission.
##### start_techcrunch_daily_scrape: Celery task for initiating daily scraping of TechCrunch articles.
##### techcrunch_scrape_by_category: Celery task for automated scraping of TechCrunch articles based on predefined categories.
##### search_keyword: Celery task for searching TechCrunch articles by keyword.
##### scrape_articles: Celery task for scraping article content and saving it to the database.
##### extract_article_url: Celery task for extracting the final URL of an article.
##### download_images: Celery task for downloading images associated with articles.
## Troubleshooting
If encountering issues with Celery or Redis, ensure that Redis server is running and properly configured.
Check Celery logs for any errors or warnings.
## Contributing
Contributions are welcome! If you find any bugs or have suggestions for improvement, please open an issue or submit a pull request.
