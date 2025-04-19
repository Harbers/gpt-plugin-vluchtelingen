#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, json, logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from typing import Any, Dict, List
from duckduckgo_search import ddg
from zoekfilters import filter_resultaten, format_apa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vluchtelingenwerk GPT API", version="1.1.0")

def load_json_config(name: str) -> Any:
    path = os.path.join(os.path.dirname(__file__), name)
    if not os.path.isfile(path):
        logger.error(f"{name} niet gevonden")
        raise HTTPException(404, detail=f"{name} niet gevonden")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "API is actief"}

@app.get("/all_procedures")
def get_all_procedures() -> Any:
    return load_json_config("AllProcedures.json")

@app.get("/mb_instrument")
def get_mb_instrument() -> Any:
    return load_json_config("MBInstrumentInvullen.json")

@app.get("/search")
def search_endpoint(
    onderwerp: str = Query(...),
    gemeente: str = Query(...),
    thuisland: str = Query(...),
    moedertaal: str = Query(...)
) -> List[Dict[str, Any]]:
    zoekterm = f"{onderwerp} {gemeente} {thuisland} {moedertaal} vluchtelingenwerk"
    logger.info(f"Zoekterm: {zoekterm}")

    # haal top 10 resultaten op
    raw = ddg(zoekterm, region='nl', safesearch='Off', max_results=10)
    now = datetime.utcnow().strftime("%Y, %B %d")
    resultaten = []
    for item in raw:
        titel = item.get("title", "")
        link  = item.get("href", "")
        beschrijving = item.get("body", "")
        apa = format_apa(titel, link, now)
        resultaten.append({
            "titel": titel,
            "link": link,
            "samenvatting": beschrijving,
            "apa": apa
        })

    # filter op betrouwbare bron en relevatie
    gefilterd = filter_resultaten(resultaten)
    if not gefilterd:
        raise HTTPException(404, detail="Geen relevante resultaten gevonden")
    return gefilterd

@app.post("/generate_image")
def generate_image(prompt: str = Query(...)) -> Any:
    # passthrough
    external = "https://externe-api-beeldgeneratie.nl/generate"
    resp = requests.post(external, json={"prompt": prompt})
    if resp.status_code != 200:
        logger.error(resp.text)
        raise HTTPException(500, detail="Fout bij beeldgeneratie")
    return resp.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
