# -----------------------------
# Blackcoffer Assignment: Text Extraction & Analysis
# -----------------------------

import os
import re
import pandas as pd
import time
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests

# -----------------------------
# Step 0: NLTK Setup
# -----------------------------
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords

# -----------------------------
# Step 1: Paths
# -----------------------------
DATA_FOLDER = "data"
ARTICLES_FOLDER = "articles"
STOPWORDS_FOLDER = "stopwords"
MASTERS_FOLDER = "masterdict"

INPUT_FILE = os.path.join(DATA_FOLDER, "Input.xlsx")
OUTPUT_FILE = os.path.join(DATA_FOLDER, "output.xlsx")
OUTPUT_TEMPLATE = os.path.join(DATA_FOLDER, "Output Data Structure.xlsx")

os.makedirs(ARTICLES_FOLDER, exist_ok=True)

# -----------------------------
# Step 2: Load Input
# -----------------------------
df_input = pd.read_excel(INPUT_FILE)

# -----------------------------
# Step 3: Load Stopwords
# -----------------------------
stop_words = set()
for file in os.listdir(STOPWORDS_FOLDER):
    if file.endswith(".txt"):
        with open(os.path.join(STOPWORDS_FOLDER, file), "r", encoding="utf-8") as f:
            stop_words.update([line.strip().lower() for line in f])

# -----------------------------
# Step 4: Load Master Dictionary
# -----------------------------
positive_words = set()
negative_words = set()
for file in os.listdir(MASTERS_FOLDER):
    path = os.path.join(MASTERS_FOLDER, file)
    with open(path, "r", encoding="utf-8") as f:
        words = [line.strip().lower() for line in f if line.strip()]
    if "positive" in file.lower():
        positive_words.update(words)
    elif "negative" in file.lower():
        negative_words.update(words)

# -----------------------------
# Step 5: Helper Functions
# -----------------------------
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def count_syllables(word):
    word = word.lower()
    vowels = "aeiou"
    count = 0
    if len(word) == 0:
        return 0
    if word[0] in vowels:
        count += 1
    for i in range(1, len(word)):
        if word[i] in vowels and word[i - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count

def personal_pronouns(text):
    pronouns = re.findall(r'\b(I|we|my|ours|us)\b', text, flags=re.I)
    return len(pronouns)

def extract_article_text(url):
    """Try Selenium first; if fails, fallback to requests + BeautifulSoup"""
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Try specific Blackcoffer content selectors
        content_div = (
            soup.find("div", class_="td-post-content") or
            soup.find("div", class_="entry-content") or
            soup.find("article")
        )

        if content_div:
            paragraphs = content_div.find_all("p")
        else:
            paragraphs = soup.find_all("p")

        title = soup.title.string.strip() if soup.title else ""
        text = title + " " + " ".join([p.get_text() for p in paragraphs])
        return clean_text(text)

    except Exception:
        # fallback using requests
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        paragraphs = soup.find_all("p")
        title = soup.title.string.strip() if soup.title else ""
        text = title + " " + " ".join([p.get_text() for p in paragraphs])
        return clean_text(text)

# -----------------------------
# Step 6: Selenium Setup
# -----------------------------
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# -----------------------------
# Step 7: Process Each URL
# -----------------------------
output_rows = []

for idx, row in df_input.iterrows():
    url_id = row["URL_ID"]
    url = row["URL"]
    print(f"Processing URL_ID: {url_id}")

    try:
        text = extract_article_text(url)

        if len(text) < 100:
            print(f"⚠️ {url_id}: Short or invalid article (len={len(text)})")
            continue

        print(f"✅ {url_id} | Sample: {text[:120]}...")

        # Save text file
        with open(os.path.join(ARTICLES_FOLDER, f"{url_id}.txt"), "w", encoding="utf-8") as f:
            f.write(text)

        # ---- Text Analysis ----
        tokens = word_tokenize(text.lower())
        tokens_clean = [t for t in tokens if t.isalpha() and t not in stop_words]

        if not tokens_clean:
            continue

        pos_score = sum(1 for t in tokens_clean if t in positive_words)
        neg_score = sum(1 for t in tokens_clean if t in negative_words)
        neg_score = neg_score * -1

        polarity = (pos_score - abs(neg_score)) / ((pos_score + abs(neg_score)) + 1e-6)
        subjectivity = (pos_score + abs(neg_score)) / (len(tokens_clean) + 1e-6)

        sentences = sent_tokenize(text)
        avg_sent_len = len(tokens_clean) / len(sentences) if sentences else 0

        complex_words = [w for w in tokens_clean if count_syllables(w) > 2]
        perc_complex = len(complex_words) / len(tokens_clean)
        fog_index = 0.4 * (avg_sent_len + perc_complex * 100)

        avg_words_per_sentence = avg_sent_len
        complex_word_count = len(complex_words)
        word_count = len(tokens_clean)
        syllables_per_word = sum(count_syllables(w) for w in tokens_clean) / word_count
        personal = personal_pronouns(text)
        avg_word_len = sum(len(w) for w in tokens_clean) / word_count

        output_rows.append({
            "URL_ID": url_id,
            "URL": url,
            "POSITIVE SCORE": pos_score,
            "NEGATIVE SCORE": abs(neg_score),
            "POLARITY SCORE": polarity,
            "SUBJECTIVITY SCORE": subjectivity,
            "AVG SENTENCE LENGTH": avg_sent_len,
            "PERCENTAGE OF COMPLEX WORDS": perc_complex,
            "FOG INDEX": fog_index,
            "AVG NUMBER OF WORDS PER SENTENCE": avg_words_per_sentence,
            "COMPLEX WORD COUNT": complex_word_count,
            "WORD COUNT": word_count,
            "SYLLABLE PER WORD": syllables_per_word,
            "PERSONAL PRONOUNS": personal,
            "AVG WORD LENGTH": avg_word_len
        })

    except Exception as e:
        print(f"❌ Error processing {url_id}: {e}")
        continue

# -----------------------------
# Step 8: Save Output
# -----------------------------
driver.quit()
df_output = pd.DataFrame(output_rows)

template = pd.read_excel(OUTPUT_TEMPLATE)
template_cols = [c.strip() for c in template.columns]

for col in template_cols:
    if col not in df_output.columns:
        df_output[col] = 0

df_output = df_output[template_cols]

try:
    df_output.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Output saved to {OUTPUT_FILE}")
except PermissionError:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    alt_path = os.path.join(DATA_FOLDER, f"output_{timestamp}.xlsx")
    df_output.to_excel(alt_path, index=False)
    print(f"⚠️ Excel locked — saved instead as {alt_path}")
