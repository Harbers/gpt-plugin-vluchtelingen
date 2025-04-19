#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from typing import Any, Dict, List
from duckduckgo_search import ddg
from zoekfilters import filter_resultaten, format_apa

# Logging configuratie
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vluchtelingenwerk GPT API", version="1.1.0")


def load_json_config(name: str) -> Any:
    """
    Laadt een JSON-configuratiebestand vanuit de projectroot.
    """
    path = os.path.join(os.path.dirname(__file__), name)
    if not os.path.isfile(path):
        logger.error(f"{name} niet gevonden")
        raise HTTPException(status_code=404, detail=f"{name} niet gevonden")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fout bij het laden van {name}: {e}")
        raise HTTPException(status_code=500, detail=f"Fout bij het laden van {name}")


@app.get("/")
def root() -> Dict[str, str]:
    """
    Healthcheck endpoint.
    """
    return {"status": "API is actief"}


@app.get("/all_procedures")
def get_all_procedures() -> Any:
    """
    Endpoint dat alle juridische procedures retourneert.
    """
    return load_json_config("AllProcedures.json")


@app.get("/mb_instrument")
def get_mb_instrument() -> Any:
    """
    Endpoint dat het MB‑Instrument retourneert.
    """
    return load_json_config("MBInstrumentInvullen.json")


@app.get("/search")
def search_endpoint(
    onderwerp: str = Query(..., description="Onderwerp om op te zoeken"),
    gemeente: str = Query(..., description="Ingevoerde gemeente"),
    thuisland: str = Query(..., description="Ingevoerde thuisland"),
    moedertaal: str = Query(..., description="Ingevoerde moedertaal")
) -> List[Dict[str, Any]]:
    """
    Voert een internetzoekopdracht uit en filtert de resultaten.
    """
    zoekterm = f"{onderwerp} {gemeente} {thuisland} {moedertaal} vluchtelingenwerk"
    logger.info(f"Uitgevoerde zoekterm: {zoekterm}")

    # Gebruik DuckDuckGo voor search
    try:
        raw_results = ddg(zoekterm, region='nl', safesearch='Off', max_results=10) or []
    except Exception as e:
        logger.error(f"Fout bij ddg-search: {e}")
        raise HTTPException(status_code=500, detail="Fout bij het uitvoeren van de zoekopdracht")

    now = datetime.utcnow().strftime("%Y, %B %d")
    resultaten = []
    for item in raw_results:
        titel = item.get("title", "")
        link = item.get("href", "")
        beschrijving = item.get("body", "")
        apa = format_apa(titel, link, now)
        resultaten.append({
            "titel": titel,
            "link": link,
            "samenvatting": beschrijving,
            "apa": apa
        })

    gefilterd = filter_resultaten(resultaten)
    if not gefilterd:
        raise HTTPException(status_code=404, detail="Geen relevante resultaten gevonden")
    return gefilterd


@app.post("/generate_image")
def generate_image(prompt: str = Query(..., description="Prompt voor beeldgeneratie")) -> Any:
    """
    Proxy naar externe beeldgeneratie-API.
    """
    api_url = "https://externe-api-beeldgeneratie.nl/generate"
    try:
        resp = requests.post(api_url, json={"prompt": prompt})
        if resp.status_code != 200:
            logger.error(f"Beeldgeneratie faalde: {resp.text}")
            raise HTTPException(status_code=500, detail="Fout bij beeldgeneratie")
        return resp.json()
    except Exception as e:
        logger.error(f"Exception bij beeldgeneratie: {e}")
        raise HTTPException(status_code=500, detail="Fout bij beeldgeneratie")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
