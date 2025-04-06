#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Response, HTTPException, Query
import json
import os
from duckduckgo_search import DDGS
from zoekfilters import filter_resultaten  # Zorg dat deze functie beschikbaar is

app = FastAPI()

def load_json(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def internet_check_procedure(query: str) -> dict:
    """
    Voert als eerste stap een internetzoekopdracht uit om de meest up-to-date informatie over de procedure te vinden.
    Valideert de gevonden resultaten op basis van betrouwbare bronnen en relevante trefwoorden.
    Indien geen betrouwbaar resultaat wordt gevonden, wordt er met een fallback-zoekopdracht gezocht.
    """
    # Eerste zoekopdracht met de oorspronkelijke query
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    valid_results = filter_resultaten(results)
    if valid_results:
        return valid_results[0]
    else:
        # Fallback zoekopdracht: voeg "nieuwste" toe aan de query
        fallback_query = "nieuwste " + query
        with DDGS() as ddgs:
            results = list(ddgs.text(fallback_query, max_results=5))
        valid_results = filter_resultaten(results)
        if valid_results:
            return valid_results[0]
        else:
            return {"error": "Geen betrouwbare informatie gevonden."}

@app.get("/search")
def search_endpoint(onderwerp: str = Query(..., description="Het onderwerp om op te zoeken")):
    """
    Voert als eerste stap een gecontroleerde internetcheck uit voor de meest actuele werkwijze.
    Als betrouwbare informatie gevonden wordt, wordt deze direct teruggegeven.
    """
    latest_info = internet_check_procedure(onderwerp)
    if "error" in latest_info:
        raise HTTPException(status_code=404, detail=latest_info["error"])
    return [latest_info]

@app.get("/startmenu")
def startmenu():
    try:
        menu = load_json("JuridischeProcedure.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JuridischeProcedure.json bestand niet gevonden.")
    return menu

@app.get("/AllProcedures.json")
def get_all_procedures():
    try:
        data = load_json("AllProcedures.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="AllProcedures.json bestand niet gevonden.")
    return data

@app.get("/MBInstrumentInvullen.json")
def get_mb_instrument():
    try:
        data = load_json("MBInstrumentInvullen.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="MBInstrumentInvullen.json bestand niet gevonden.")
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
