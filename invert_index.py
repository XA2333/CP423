import os
import re
import nltk
from nltk.corpus import stopwords
from collections import defaultdict

# Make sure stopwords are available
nltk.download('stopwords')

# Directory containing scraped text files
INPUT_DIR = "scraped_pages"
OUTPUT_FILE = "inverted_index.txt"

# Load English stopwords
stop_words = set(stopwords.words('english'))

# Inverted index structure: term → set of filenames
inverted_index = defaultdict(set)

def preprocess_text(text):
    """
    Preprocess the input text:
    - Convert to lowercase
    - Use regex to tokenize (extract alphanumeric words)
    - Remove stopwords and single-character terms
    """
    text = text.lower()
    # Use regex to extract words (alphanumeric only)
    tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text)
    cleaned = [token for token in tokens if token not in stop_words and len(token) > 1]
    return cleaned

def build_index():
    """
    Build an inverted index from all files in INPUT_DIR.
    """
    for filename in os.listdir(INPUT_DIR):
        filepath = os.path.join(INPUT_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
            tokens = preprocess_text(text)
            for token in tokens:
                inverted_index[token].add(filename)

    # Write the inverted index to a text file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for term in sorted(inverted_index):
            doc_list = ", ".join(sorted(inverted_index[term]))
            out.write(f"{term}: {doc_list}\n")

if __name__ == "__main__":
    build_index()
    print(f"Inverted index written to {OUTPUT_FILE}. Total terms: {len(inverted_index)}")
