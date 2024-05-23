import requests
from bs4 import BeautifulSoup
import json
from db import save_article, is_article_sent

SITES = [
    'https://techcrunch.com/',
    'https://www.theverge.com/',
    'https://www.wired.com/'
]

def load_keywords():
    with open('keywords.json', 'r') as f:
        data = json.load(f)
    return data['keywords']

def scrape_site(url):
    try:
        print(f"Scraping site: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []
        if 'techcrunch' in url:
            articles = scrape_techcrunch(soup)
        elif 'theverge' in url:
            articles = scrape_theverge(soup)
        elif 'wired' in url:
            articles = scrape_wired(soup)

        return articles
    except Exception as e:
        print(f"Probleme de scraping sur {url}: {e}")
        return []

def scrape_techcrunch(soup):
    keywords = load_keywords()
    articles = []
    try:
        for item in soup.find_all('a', attrs={'data-module': 'Post Title'}):
            title = item.get_text(strip=True)
            link = item['href']
            category_tag = item.find_previous('a', class_='is-taxonomy-category')
            if category_tag:
                category = category_tag.get_text(strip=True).lower()
                if any(keyword.lower() in category for keyword in keywords):
                    if not is_article_sent(link):
                        print(f"TechCrunch Article: {title} - {link} - Category: {category}")
                        articles.append((title, link))
                        save_article(link)
    except Exception as e:
        print(f"Erreur de scraping sur le site techcrunch: {e}")
    return articles

def scrape_theverge(soup):
    keywords = load_keywords()
    articles = []
    try:
        for item in soup.find_all('a', class_='after:absolute after:inset-0 group-hover:shadow-underline-blurple dark:group-hover:shadow-underline-franklin'):
            title = item.get_text(strip=True)
            relative_link = item['href']
            link = f"https://www.theverge.com{relative_link}"
            category_tag = item.find_previous('span', class_='duet--content-cards--content-card-group')
            if category_tag:
                category_link = category_tag.find('a')
                if category_link:
                    category = category_link.get_text(strip=True).lower()
                    if any(keyword.lower() in category for keyword in keywords):
                        if not is_article_sent(link):
                            print(f"The Verge Article: {title} - {link} - Category: {category}")
                            articles.append((title, link))
                            save_article(link)
    except Exception as e:
        print(f"Erreur de scraping sur le site The Verge: {e}")
    return articles

def scrape_wired(soup):
    keywords = load_keywords()
    articles = []
    try:
        for item in soup.find_all('a', class_=['SubtopicDiscoverySubsequentHed', 'SubtopicDiscoveryFirstHed']):
            title_tag = item.find('h2')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = f"https://www.wired.com{item['href']}"
                category_tag = item.find_previous(['span', 'a'], class_='RubricName-fVtemz cLxcNi rubric__name')
                if category_tag:
                    category = category_tag.get_text(strip=True).lower()
                    if any(keyword.lower() in category for keyword in keywords):
                        if not is_article_sent(link):
                            print(f"Wired Article: {title} - {link} - Category: {category}")
                            articles.append((title, link))
                            save_article(link)
    except Exception as e:
        print(f"Erreur de scraping sur le site Wired: {e}")
    return articles


def scrape_all_sites():
    all_articles = []
    for site in SITES:
        articles = scrape_site(site)
        all_articles.extend(articles)
    return all_articles
