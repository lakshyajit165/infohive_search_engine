import requests
from bs4 import BeautifulSoup
import os


def fetch_rss_feed(url):
    """Fetches and parses RSS feed, returning list of article URLs."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    links = soup.find_all('link')[1:]  # Skip the first 'link' as it's the link to the RSS itself
    return [link.text for link in links]

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

def save_content(source_folder, title, content):
    """Saves content to a text file named after the title."""
    try: 
        # null check for filename
        if len(title) > 0:
            safe_title = "".join(x for x in title if x.isalnum() or x in " -_")
            filename = f"{safe_title}.txt"
            filepath = os.path.join(source_folder, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    except Exception as e:
        print(f"Error saving file with title {title}: {e}")

def main():
    rss_urls = [
        'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
        'https://timesofindia.indiatimes.com/rssfeedmostrecent.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/296589292.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/7098551.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/1898055.cms',
        'https://timesofindia.indiatimes.com/rssfeeds_us/72258322.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/54829575.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/4719148.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/-2128672765.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/2647163.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/66949542.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/913168846.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/2886704.cms'
    ]
    for rss_url in rss_urls:
        article_urls = fetch_rss_feed(rss_url)
        for url in article_urls:
            if len(url) > 0:
                title, content = scrape_article(url)
                save_content("source_files", title, content)
                if len(title) > 0: 
                    print(f"Saved '{title}' to file.")

if __name__ == "__main__":
    main()
