from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from duckduckgo_search import DDGS
import json

app = FastAPI()

# Serve .well-known for ai-plugin.json
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")

# Laad zoektermen en onderwerpen
with open("ZoekenInternet.json", encoding="utf-8") as f:
    bronnen = json.load(f)

@app.get("/search")
def zoek(onderwerp: str = Query(..., description="Het onderwerp om op te zoeken")):
    zoektermen = bronnen.get(onderwerp, [])
    resultaten = []
    with DDGS() as ddgs:
        for term in zoektermen:
            for r in ddgs.text(term, max_results=3):
                resultaten.append({
                    "title": r.get("title"),
                    "href": r.get("href"),
                    "body": r.get("body")
                })
    return resultaten[:10]