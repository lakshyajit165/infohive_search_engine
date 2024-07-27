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
    title_tag = soup.find('h1', class_='sc-518485e5-0 bWszMR')
    # make title empty if no title tag is present
    title = title_tag.text.strip() if title_tag else ''


    # print("content: ", content)
    paragraphs = soup.find_all('p', class_='sc-eb7bd5f6-0 fYAfXe')
    # Extract text from each <p> tag and combine into a single string
    if paragraphs:
        content = ' '.join(p.get_text(strip=True) for p in paragraphs) if paragraphs else 'No Content'
    else:
        content = 'No Content'
    
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
        'https://feeds.bbci.co.uk/news/world/rss.xml', # world
        'https://feeds.bbci.co.uk/news/business/rss.xml', # business
        'https://feeds.bbci.co.uk/news/politics/rss.xml', # politics
        'https://feeds.bbci.co.uk/news/health/rss.xml', # health
        'https://feeds.bbci.co.uk/news/education/rss.xml', # education
        'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml', # science_and_environment
        'https://feeds.bbci.co.uk/news/technology/rss.xml', # technology
        'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml' # entertainment_and_arts
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
