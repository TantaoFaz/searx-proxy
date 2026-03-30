from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

INSTANCES = [
    "https://searx.ox2.fr",
    "https://searx.sev.monster",
    "https://searx.fmhy.net",
]
HEADERS = {"User-Agent": "Mozilla/5.0"}

def try_rss(instance, q, engines):
    r = requests.get(
        f"{instance}/search",
        params={"q": q, "engines": engines, "format": "rss"},
        headers=HEADERS,
        timeout=6
    )
    if r.status_code != 200:
        return None
    root = ET.fromstring(r.text)
    ns = {"media": "http://search.yahoo.com/mrss/"}
    results = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "")
        url   = item.findtext("link", "")
        desc  = item.findtext("description", "")
        results.append({"title": title, "url": url, "content": desc, "source": instance})
    return results

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    engines = request.args.get("engines", "google,duckduckgo")
    if not q:
        return jsonify({"error": "missing query"}), 400
    for inst in INSTANCES:
        try:
            results = try_rss(inst, q, engines)
            if results is not None:
                return jsonify({"query": q, "results": results, "instance": inst})
        except:
            continue
    return jsonify({"error": "all instances failed"}), 503

@app.route("/")
def index():
    return jsonify({"status": "ok", "usage": "/search?q=query"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
