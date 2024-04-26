import os
from bs4 import BeautifulSoup
import requests
import threading


# Function to fetch data from Wikipedia API and store it in a text file
def fetch_and_store_wikipedia_data(topic, filename):
    # Wikipedia API endpoint for full content
    api_url = f"https://en.wikipedia.org/api/rest_v1/page/html/{topic}"
    
    try:
        # Make GET request to Wikipedia API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text content from the HTML
        text_content = soup.get_text()

        # Create directory if it does not exist
        os.makedirs("source_files", exist_ok=True)

        # Write content to text file with exact topic name as filename
        with open(os.path.join("source_files", filename), "w", encoding="utf-8") as file:
            file.write(text_content)

        print(f"Data for '{topic}' stored in '{filename}'")
    except Exception as e:
        print(f"Error fetching or storing data for '{topic}': {e}")

# Function to fetch Wikipedia data for multiple topics using multiple threads
def fetch_data_for_topics(topics):
    threads = []
    for topic, filename in topics:
        thread = threading.Thread(target=fetch_and_store_wikipedia_data, args=(topic, filename))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

# Read topics from file
def read_topics_from_file(filename):
    with open(filename, "r") as file:
        topics = [line.strip() for line in file if line.strip()]
    return topics

topics = read_topics_from_file("topics.txt")
filenames = [topic.replace(" ", "_").lower() + ".txt" for topic in topics]  # Modify filenames
topics_with_filenames = list(zip(topics, filenames))
fetch_data_for_topics(topics_with_filenames)

