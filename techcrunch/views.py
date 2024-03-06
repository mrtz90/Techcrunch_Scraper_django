from django.shortcuts import render
from django.db.models import Count

import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from techcrunch.models import Article


matplotlib.use('Agg')


def get_article_counts_by_category():
    """
    Fetches the count of articles in each category.
    """
    article_counts = (
        Article.objects
        .values('category__title')
        .annotate(count=Count('id'))
        .order_by('category__title')
    )
    print(article_counts)
    return article_counts


def generate_category_chart(article_counts):
    categories = [item['category__title'] for item in article_counts]
    counts = [item['count'] for item in article_counts]

    plt.bar(categories, counts)
    plt.xlabel('Category')
    plt.ylabel('Number of Articles')
    plt.title('Article Counts by Category')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('techcrunch/static/article_counts_by_category.png')


def article_report(request):
    article_counts = get_article_counts_by_category()
    generate_category_chart(article_counts)
    # Generate word cloud and get file path
    generate_word_cloud()
    return render(request, 'article_report.html')


def generate_word_cloud():
    # Sample article summaries (replace this with your actual data retrieval)
    article_summaries = Article.objects.values_list('summary', flat=True)
    # Combine all summaries into a single string
    text = ' '.join(article_summaries)

    # Generate word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Save word cloud as image file
    wordcloud_path = 'techcrunch/static/wordcloud.png'  # Specify the file path where you want to save the image
    wordcloud.to_file(wordcloud_path)

    return wordcloud_path
