#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from typing import Any, Dict, List
from duckduckgo_search import ddg
import requests

from zoekfilters import filter_resultaten, format_apa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vluchtelingenwerk GPT API", version="1.1.0")

def load_json_config(filename: str) -> Any:
    path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.isfile(path):
        logger.error(f"{filename} niet gevonden")
        raise HTTPException(status_code=404, detail=f"{filename} niet gevonden")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fout bij laden {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Fout bij laden {filename}")

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
    onderwerp: str = Query(..., description="Onderwerp om op te zoeken"),
    gemeente: str = Query(..., description="Gemeente van de cliënt"),
    thuisland: str = Query(..., description="Thuisland van de cliënt"),
    moedertaal: str = Query(..., description="Moedertaal van de cliënt")
) -> List[Dict[str, Any]]:
    zoekterm = f"{onderwerp} {gemeente} {thuisland} {moedertaal} vluchtelingenwerk"
    logger.info(f"Uitgevoerde zoekterm: {zoekterm}")

    raw_results = ddg(zoekterm, region="nl", safesearch="Off", max_results=10)
    if not raw_results:
        raise HTTPException(status_code=404, detail="Geen zoekresultaten gevonden")

    now = datetime.utcnow().strftime("%Y, %B %d")
    resultaten = []
    for item in raw_results:
        titel = item.get("title", "")
        link  = item.get("href", "")
        samenv = item.get("body", "")
        apa = format_apa(titel, link, now)
        resultaten.append({
            "titel": titel,
            "link": link,
            "samenvatting": samenv,
            "apa": apa
        })

    gefilterd = filter_resultaten(resultaten)
    if not gefilterd:
        raise HTTPException(status_code=404, detail="Geen relevante resultaten na filteren")

    return gefilterd

@app.post("/generate_image")
def generate_image(prompt: str = Query(..., description="Prompt voor beeldgeneratie")) -> Any:
    api_url = "https://externe-api-beeldgeneratie.nl/generate"
    try:
        resp = requests.post(api_url, json={"prompt": prompt})
        if resp.status_code != 200:
            logger.error(f"Beeldgeneratie error: {resp.text}")
            raise HTTPException(status_code=500, detail="Fout bij beeldgeneratie")
        return resp.json()
    except Exception as e:
        logger.error(f"Fout in beeldgeneratie-call: {e}")
        raise HTTPException(status_code=500, detail="Fout bij beeldgeneratie")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
