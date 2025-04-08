#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vluchtelingenzoeker API – Backend
Deze module bevat de FastAPI-applicatie met endpoints voor het uitvoeren van
zoekopdrachten en het aanbieden van het MB‑Instrument.
"""

import json
import os
import logging
from fastapi import FastAPI, HTTPException, Query, Response
from typing import Any, Dict, List
from duckduckgo_search import ddg
from zoekfilters import filter_resultaten

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vluchtelingenzoeker API", version="2.0.0")

def load_json(file_path: str) -> Any:
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
    gemeente: str = Query(None),
    thuisland: str = Query(None),
    moedertaal: str = Query(None)
) -> List[Dict[str, str]]:
    """
    Voert een zoekopdracht uit via DuckDuckGo voor het opgegeven onderwerp,
    en filtert de resultaten met zoekfilters.py.
    """
    # U zou hier ook ZoekenInternet.json kunnen inlezen als u daar nog iets mee doet,
    # of direct 'onderwerp' gebruiken.
    try:
        # Voorbeeld: direct zoeken op 'onderwerp'
        term = f"{onderwerp} {gemeente or ''} {thuisland or ''} {moedertaal or ''}".strip()
        search_results = []
        for r in ddg(term, max_results=5):
            resultaat = {
                "titel": r.get("title", ""),
                "link": r.get("href", ""),
                "samenvatting": r.get("body", "")
            }
            search_results.append(resultaat)
    except Exception as e:
        logger.error(f"Fout bij het uitvoeren van de zoekopdracht: {e}")
        raise HTTPException(status_code=500, detail="Fout bij het uitvoeren van de zoekopdracht.")
    
    gefilterde_resultaten = filter_resultaten(search_results)
    if not gefilterde_resultaten:
        logger.info("Geen relevante updates gevonden.")
        raise HTTPException(status_code=404, detail="Geen relevante updates gevonden.")
    
    return gefilterde_resultaten

@app.get("/mb_instrument")
def get_mb_instrument() -> Any:
    """
    Haal de data op voor het MB‑Instrument (MBInstrumentInvullen.json).
    """
    try:
        data = load_json("MBInstrumentInvullen.json")
        return data
    except FileNotFoundError:
        logger.error("MBInstrumentInvullen.json bestand niet gevonden.")
        raise HTTPException(status_code=404, detail="MBInstrumentInvullen.json bestand niet gevonden.")

# De onderstaande endpoints zijn optioneel als u procedures niet meer via de backend aanbiedt.
@app.get("/all_procedures")
def get_all_procedures() -> Any:
    try:
        data = load_json("AllProcedures.json")
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="AllProcedures.json bestand niet gevonden.")

@app.get("/startmenu")
def get_startmenu() -> Any:
    try:
        data = load_json("AllProcedures.json")
        startmenu_data = {key: data.get(key) for key in ["startVraag", "basisgegevens", "menu"]}
        return startmenu_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="AllProcedures.json bestand niet gevonden.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
