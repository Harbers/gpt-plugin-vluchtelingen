#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vluchtelingenzoeker API – backend.
Deze module bevat de FastAPI-applicatie met endpoints voor het ophalen
van juridische/maatschappelijke procedures, het uitvoeren van zoekopdrachten en het ophalen van het MB‑Instrument.
"""

import json
import os
import logging
from fastapi import FastAPI, Response, HTTPException, Query
from typing import Any, Dict, List
from duckduckgo_search import ddg  # gebruik ddg() voor zoekopdrachten
from zoekfilters import filter_resultaten

# Logging configuratie
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vluchtelingenzoeker API", version="1.1.0")

def load_json(file_path: str) -> Any:
    if not os.path.isfile(file_path):
        logger.error(f"Bestand niet gevonden: {file_path}")
        raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
def start() -> Dict[str, str]:
    return {"status": "API is actief"}

@app.head("/")
def head_root() -> Response:
    return Response(status_code=200)

@app.get("/search")
def search_endpoint(
    onderwerp: str = Query(..., description="Het onderwerp om op te zoeken"),
    gemeente: str = Query(None, description="Optionele gemeentelijke input voor filtering"),
    thuisland: str = Query(None, description="Optionele input over het thuisland"),
    moedertaal: str = Query(None, description="Optionele invoer van de moedertaal")
) -> List[Dict[str, str]]:
    try:
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

@app.get("/startmenu")
def startmenu() -> Any:
    try:
        # Gebruik het master-bestand voor procedures.
        menu = load_json("AllProcedures.json")
    except FileNotFoundError:
        logger.error("AllProcedures.json bestand niet gevonden.")
        raise HTTPException(status_code=404, detail="AllProcedures.json bestand niet gevonden.")
    return menu

@app.get("/all_procedures")
def get_all_procedures() -> Any:
    try:
        data = load_json("AllProcedures.json")
    except FileNotFoundError:
        logger.error("AllProcedures.json bestand niet gevonden.")
        raise HTTPException(status_code=404, detail="AllProcedures.json bestand niet gevonden.")
    return data

@app.get("/mb_instrument")
def get_mb_instrument() -> Any:
    try:
        data = load_json("MBInstrumentInvullen.json")
    except FileNotFoundError:
        logger.error("MBInstrumentInvullen.json bestand niet gevonden.")
        raise HTTPException(status_code=404, detail="MBInstrumentInvullen.json bestand niet gevonden.")
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
