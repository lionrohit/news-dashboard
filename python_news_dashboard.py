from flask import Flask, render_template
import feedparser
import requests
import re

app = Flask(__name__)

# Clean HTML
def clean_html(raw_text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', raw_text)

# Extract image if available
def extract_image(entry):
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    elif 'links' in entry:
        for link in entry.links:
            if link.type.startswith('image'):
                return link.href
    return None

def get_news():
    sources = [
        {
            "name": "Indian Express",
            "url": "https://indianexpress.com/feed/"
        },
        {
            "name": "Financial Express",
            "url": "https://www.financialexpress.com/feed/"
        },
        {
            "name": "Mint",
            "url": "https://www.livemint.com/rss/news"
        },
        {
            "name": "Hindustan Times",
            "url": "https://www.hindustantimes.com/feeds/rss/topnews/rssfeed.xml"
        }
    ]

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    articles = []

    for source in sources:
        response = requests.get(source["url"], headers=headers)
        feed = feedparser.parse(response.content)

        for entry in feed.entries[:3]:
            summary = ""

            if hasattr(entry, "summary"):
                summary = entry.summary
            elif hasattr(entry, "description"):
                summary = entry.description
            else:
                summary = "No summary available"

            summary = clean_html(summary)

            image = extract_image(entry)

            articles.append({
                "source": source["name"],
                "title": entry.title,
                "summary": summary,
                "link": entry.link,
                "image": image
            })

    return articles


@app.route("/")
def home():
    news = get_news()
    return render_template("index.html", news=news)


if __name__ == "__main__":
    app.run(debug=True)