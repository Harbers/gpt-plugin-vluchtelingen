#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vluchtelingenzoeker API – Backend
Deze module bevat de FastAPI-applicatie met endpoints voor het ophalen van juridische en maatschappelijke procedures,
het uitvoeren van zoekopdrachten en het aanbieden van het MB‑Instrument en het startmenu (AllProcedures.json).
"""

import json
import os
import logging
from fastapi import FastAPI, HTTPException, Query, Response
from typing import Any, Dict, List
from duckduckgo_search import ddg  # Gebruik ddg() voor zoekopdrachten
from zoekfilters import filter_resultaten

# Logging configuratie
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vluchtelingenzoeker API", version="1.2.0")

def load_json(file_path: str) -> Any:
    """Laadt een JSON-bestand en retourneert de inhoud."""
    if not os.path.isfile(file_path):
        logger.error(f"Bestand niet gevonden: {file_path}")
        raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "API is actief"}

@app.head("/")
def head_root() -> Response:
    return Response(status_code=200)

@app.get("/search")
def search_endpoint(
    onderwerp: str = Query(..., description="Het onderwerp om op te zoeken"),
    gemeente: str = Query(None, description="Optionele gemeentelijke informatie"),
    thuisland: str = Query(None, description="Optionele informatie over het thuisland"),
    moedertaal: str = Query(None, description="Optionele invoer van de moedertaal")
) -> List[Dict[str, str]]:
    """
    Voert een zoekopdracht uit via DuckDuckGo op basis van een onderwerp, met optionele extra parameters.
    De zoekopdracht wordt aanvullend samengesteld met informatie (bijv. gemeente, thuisland, moedertaal) en
    vervolgens gefilterd op betrouwbaarheid.
    """
    try:
        # Gebruik AllProcedures.json als centrale bron voor zoekresultaten
        with open("AllProcedures.json", encoding="utf-8") as f:
            bronnen = json.load(f)
    except FileNotFoundError:
        logger.error("AllProcedures.json bestand niet gevonden.")
        raise HTTPException(status_code=404, detail="AllProcedures.json bestand niet gevonden.")
    
    zoekresultaten = bronnen.get(onderwerp, [])
    if not zoekresultaten:
        logger.error(f"Geen zoekresultaten gevonden voor onderwerp: {onderwerp}")
        raise HTTPException(status_code=404, detail=f"Geen zoekresultaten gevonden voor onderwerp: {onderwerp}")
    
    resultaten: List[Dict[str, str]] = []
    try:
        zoekterm = f"{onderwerp} {gemeente or ''} {thuisland or ''} {moedertaal or ''}".strip()
        for item in zoekresultaten:
            term = f"{item.get('sourceTitle', '')} {item.get('description', '')} {zoekterm}"
            for r in ddg(term, max_results=3):
                resultaat = {
                    "titel": r.get("title", ""),
                    "link": r.get("href", ""),
                    "samenvatting": r.get("body", "")
                }
                resultaten.append(resultaat)
    except Exception as e:
        logger.error(f"Fout bij het uitvoeren van de zoekopdracht: {e}")
        raise HTTPException(status_code=500, detail="Fout bij het uitvoeren van de zoekopdracht.")
    
    gefilterde_resultaten = filter_resultaten(resultaten)
    if not gefilterde_resultaten:
        logger.error("Geen relevante updates gevonden.")
        raise HTTPException(status_code=404, detail="Geen relevante updates gevonden.")
    
    return gefilterde_resultaten[:10]

@app.get("/all_procedures")
def get_all_procedures() -> Any:
    """Haal de volledige set juridische en maatschappelijke procedures op (AllProcedures.json)."""
    try:
        data = load_json("AllProcedures.json")
        return data
    except FileNotFoundError:
        logger.error("AllProcedures.json bestand niet gevonden.")
        raise HTTPException(status_code=404, detail="AllProcedures.json bestand niet gevonden.")

@app.get("/mb_instrument")
def get_mb_instrument() -> Any:
    """Haal de data op voor het MB‑Instrument (MBInstrumentInvullen.json)."""
    try:
        data = load_json("MBInstrumentInvullen.json")
        return data
    except FileNotFoundError:
        logger.error("MBInstrumentInvullen.json bestand niet gevonden.")
        raise HTTPException(status_code=404, detail="MBInstrumentInvullen.json bestand niet gevonden.")

@app.get("/startmenu")
def get_startmenu() -> Any:
    """
    Haal het startmenu op, d.w.z. de elementen 'startVraag', 'basisgegevens' en 'menu'
    uit AllProcedures.json. Dit menu wordt bijvoorbeeld gebruikt in de frontend.
    """
    try:
        data = load_json("AllProcedures.json")
        startmenu_data = { key: data.get(key) for key in ["startVraag", "basisgegevens", "menu"] }
        return startmenu_data
    except FileNotFoundError:
        logger.error("AllProcedures.json bestand niet gevonden.")
        raise HTTPException(status_code=404, detail="AllProcedures.json bestand niet gevonden.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
