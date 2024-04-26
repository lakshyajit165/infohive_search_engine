import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

''' This method helps scrape websites and store content in the text files for our prototype'''
def fetch_and_save_website_content(url):
    try:
        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors

        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unwanted tags (e.g., script, style, meta, etc.)
        for script in soup(["script", "style", "meta", "noscript"]):
            script.decompose()  # Removes the tags

        # Get text from the remaining HTML
        text = soup.get_text(separator='\n', strip=True)

        # Generate a filename from the domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        filename = f"{domain.replace('www.', '').replace(':', '_').replace('.', '_')}.txt"
        
        # Write the parsed text to a file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Content saved to {filename}")
    except requests.RequestException as e:
        print(f"Failed to fetch data from {url}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
fetch_and_save_website_content('https://www.ibm.com/topics/machine-learning')
