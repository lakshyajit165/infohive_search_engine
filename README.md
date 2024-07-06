# Text-Based Search Engine Prototype

## Overview

This project is a prototype for a text-based search engine that ranks documents using the TF-IDF (Term Frequency-Inverse Document Frequency) scoring algorithm. The current implementation parses RSS feeds from the Times of India website, stores the articles' content in text files, and then uses these files to create an index and a vector space model. Once the index is ready, users can query it to get a list of documents ranked by their TF-IDF scores.

## Features

1. **RSS Parsing**: Parses RSS links from the Times of India website and stores the articles' content in text files.
2. **Index Creation**: Parses the text files to create an index and a vector space model for each document.
3. **TF-IDF Ranking**: Queries the index and returns a list of documents ranked according to the highest TF-IDF score.

## Project Structure

-   `rss_feed_scraper_toi.py`: Script for parsing RSS feeds and storing article contents in text files.
-   `create_index.py`: Script for creating an index and vector space model from the text files.
-   `query_index.py`: Script for querying the index and ranking documents based on TF-IDF scores.
-   `source_files/`: Directory where the text files containing article contents are stored.
-   `index.txt`: Directory where the index and vector space model files are stored.

## Usage

### Step 1: Parse RSS Feeds

Run the `rss_feed_scraper_toi.py` script to parse RSS feeds from the Times of India website and store the articles' content in text files.

```bash
python3 rss_feed_scraper_toi.py
```

### Step 2: Create the index

Run the `create_index.py` script to create an index out of the text files stored.

```bash
python3 create_index.py
```

### Step 3: Query the index

Run the `query_index.py` script with the appropriate query that you want to search. If there is any particular term that is supposed to be emphasized, wrap it in double quotes

## Note

The source_files directory can take up a lot of memory as per the current implementation. Optimizations are on the way. Stay tuned :)
