from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

INSTANCE = "https://searx.fmhy.net"
HEADERS = {"User-Agent": "Mozilla/5.0"}

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    engines = request.args.get("engines", "google,duckduckgo")

    if not q:
        return jsonify({"error": "missing query"}), 400

    try:
        r = requests.get(
            f"{INSTANCE}/search",
            params={"q": q, "engines": engines},
            headers=HEADERS,
            timeout=8
        )
        soup = BeautifulSoup(r.text, "html.parser")
        results = []

        for article in soup.select(".result"):
            title_el = article.select_one("h3 a")
            desc_el  = article.select_one(".content")
            url_el   = article.select_one(".url_wrapper, .url")

            if not title_el:
                continue

            results.append({
                "title":   title_el.get_text(strip=True),
                "url":     title_el.get("href", ""),
                "content": desc_el.get_text(strip=True) if desc_el else "",
                "source":  url_el.get_text(strip=True) if url_el else ""
            })

        return jsonify({"query": q, "results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return jsonify({"status": "ok", "usage": "/search?q=query"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
