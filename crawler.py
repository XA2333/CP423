import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL for Wikipedia
WIKI_BASE = "https://en.wikipedia.org"

# Starting Wikipedia page on Canadian provinces' historical population
START_URL = "https://en.wikipedia.org/wiki/List_of_Canadian_provinces_and_territories_by_historical_population"

# Directory to save extracted text files
SAVE_DIR = "scraped_pages"

# Set to store visited URLs to avoid duplicates
visited_urls = set()

def get_valid_links(soup):
    """
    Extracts up to 5 valid internal Wikipedia article links from the page.
    Filters out links containing colons (e.g., 'Category:', 'Help:').
    """
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag['href']
        if href.startswith("/wiki/") and ':' not in href:
            full_url = urljoin(WIKI_BASE, href)
            if full_url not in visited_urls:
                links.append(full_url)
            if len(links) >= 5:
                break
    return links

def clean_html(soup):
    """
    Cleans HTML content by removing unnecessary elements like scripts, styles,
    navigation bars, headers, footers, tables, and specific sections such as
    'References', 'See also', etc.
    """
    skip_ids = ["See_also", "References", "Bibliography", "Further_reading", "External_links"]

    # Remove common irrelevant tags
    for tag in soup(["script", "style", "header", "footer", "nav", "table"]):
        tag.decompose()

    # Remove "edit" buttons
    for span in soup.find_all("span", {"class": "mw-editsection"}):
        span.decompose()

    # Remove unwanted sections by id
    for id_ in skip_ids:
        span = soup.find("span", {"id": id_})
        if span and span.parent.name == "h2":
            for sibling in span.parent.find_next_siblings():
                sibling.decompose()

    return soup.get_text(separator="\n")

def save_text(text, url, depth):
    """
    Saves the cleaned text content to a .txt file.
    Filenames include the crawl depth and a hash of the URL for uniqueness.
    """
    filename = os.path.join(SAVE_DIR, f"depth{depth}_{hash(url)}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def crawl(url, depth, max_depth):
    """
    Recursively crawls Wikipedia pages up to a specified depth.
    Follows internal article links and avoids revisiting URLs.
    """
    if url in visited_urls or depth > max_depth:
        return
    print(f"Crawling (depth={depth}): {url}")
    visited_urls.add(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    text = clean_html(soup)
    save_text(text, url, depth)

    # Fetch and crawl up to 5 new valid internal links
    links = get_valid_links(soup)
    for link in links:
        crawl(link, depth + 1, max_depth)

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Start crawling from the root URL with max depth = 2 (i.e., 3 levels total)
    crawl(START_URL, depth=0, max_depth=2)

    print(f"Done. Total pages saved: {len(os.listdir(SAVE_DIR))}")
