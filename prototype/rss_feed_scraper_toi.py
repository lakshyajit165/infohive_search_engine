import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urlparse


def fetch_rss_feed(url):
    """Fetches and parses RSS feed, returning list of article URLs."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')
    links = [item.find('link').text for item in items if item.find('link')]
    return links

def scrape_article(url):
    """Scrapes the title and content from a given Times of India article URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title_tag = soup.find('h1', class_='HNMDR')
    # make title empty if no title tag is present
    title = title_tag.text.strip() if title_tag else ''
    
    # Extract content
    content_tag = soup.find('div', class_='_s30J clearfix')
    content = content_tag.get_text(separator=' ', strip=True) if content_tag else 'No Content'
    
    return title, content

def save_content(source_folder, url, title, content):
    """Saves content to a JSON file named after the title."""
    try: 
        # Null check for filename
        if len(title) > 0:
            # Sanitize the title to create a safe filename
            safe_title = "".join(x for x in title if x.isalnum() or x in " -_")
            filename = f"{safe_title}.json"
            filepath = os.path.join(source_folder, filename)
            
            # Create a dictionary for the content
            data = {
                "url": url,
                "title": title,
                "content": content
            }
            
            # Write the dictionary to a JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving file with title {title}: {e}")


def main():
    rss_urls = [
        'https://timesofindia.indiatimes.com/rssfeedstopstories.cms', # breaking
        'https://timesofindia.indiatimes.com/rssfeedmostrecent.cms', # breaking
        'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms', # india
        'https://timesofindia.indiatimes.com/rssfeeds/296589292.cms', # world
        'https://timesofindia.indiatimes.com/rssfeeds/1898055.cms', # business
        'https://timesofindia.indiatimes.com/rssfeeds/54829575.cms', # cricket
        'https://timesofindia.indiatimes.com/rssfeeds/4719148.cms', # sports
        'https://timesofindia.indiatimes.com/rssfeeds/-2128672765.cms', # science
        'https://timesofindia.indiatimes.com/rssfeeds/2647163.cms', # environment
        'https://timesofindia.indiatimes.com/rssfeeds/913168846.cms', # education
    ]
    for rss_url in rss_urls:
        article_urls = fetch_rss_feed(rss_url)
        for url in article_urls:
            if len(url) > 0:
                title, content = scrape_article(url)
                save_content("source_files", url, title, content)
                if len(title) > 0: 
                    print(f"Saved '{title}' to file.")

if __name__ == "__main__":
    main()
