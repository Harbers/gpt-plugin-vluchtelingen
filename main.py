#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py - Backend voor DuckDuckGo-zoekfunctionaliteit

Deze FastAPI-applicatie verzorgt uitsluitend de zoekfunctie. Op basis van een meegegeven onderwerp
wordt in het bestand 'ZoekenInternet.json' gezocht naar relevante zoektermen.
Voor iedere zoekterm wordt met behulp van de DuckDuckGo-search module actuele informatie opgehaald.
De resultaten worden als JSON teruggegeven.

Deze backend is gehost op:
    https://gpt-plugin-vluchtelingen.onrender.com

Alle procedurele stappen (menu’s, vragen, handelingsplannen, etc.) worden volledig door de frontend afgehandeld.
De backend fungeert uitsluitend als zoekmachine-brug.
"""

from fastapi import FastAPI, HTTPException, Query
import json
import os
from duckduckgo_search import DDGS

app = FastAPI(
    title="Vluchtelingen Zoekplugin Backend",
    description="Backend voor het ophalen van actuele informatie via DuckDuckGo. Gehost op https://gpt-plugin-vluchtelingen.onrender.com",
    version="1.0.0"
)

def load_json(file_path: str) -> dict:
    """
    Laadt een JSON-bestand met de gegeven file path.
    Geeft een dictionary terug.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/", summary="Controleer of de API actief is")
def root():
    """
    Basis-endpoint om te controleren of de API actief is.
    """
    return {"status": "API is actief"}

@app.get("/search", summary="Zoek actuele informatie via DuckDuckGo")
def search_endpoint(onderwerp: str = Query(..., description="Het onderwerp om op te zoeken")):
    """
    Endpoint voor het ophalen van actuele zoekresultaten via DuckDuckGo.

    Werking:
    1. Laad de zoektermen voor het gegeven onderwerp uit 'ZoekenInternet.json'.
    2. Voor iedere zoekterm worden maximaal 3 resultaten opgehaald via DuckDuckGo.
    3. De verzamelde resultaten worden als JSON teruggegeven.

    :param onderwerp: De naam van het onderwerp (bijv. 'Asielprocedure', 'Dublin', etc.)
    :return: Een lijst met zoekresultaten met titel, link en samenvatting.
    """
    try:
        zoekdata = load_json("ZoekenInternet.json")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    zoektermen = zoekdata.get(onderwerp, [])
    if not zoektermen:
        raise HTTPException(status_code=404, detail=f"Geen zoektermen gevonden voor onderwerp: {onderwerp}")

    resultaten = []
    try:
        with DDGS() as ddgs:
            for term in zoektermen:
                # Voor iedere zoekterm worden maximaal 3 resultaten opgehaald
                for result in ddgs.text(term, max_results=3):
                    resultaat = {
                        "titel": result.get("title"),
                        "link": result.get("href"),
                        "samenvatting": result.get("body")
                    }
                    resultaten.append(resultaat)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij het ophalen van zoekresultaten: {e}")

    if not resultaten:
        raise HTTPException(status_code=404, detail="Geen relevante resultaten gevonden.")
    
    return resultaten

if __name__ == "__main__":
    import uvicorn
    # Let op: bij deployment op onrender.com wordt uvicorn vaak automatisch gestart.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
