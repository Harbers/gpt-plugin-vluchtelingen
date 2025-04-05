#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Response, HTTPException, Query
import json
import os
from duckduckgo_search import DDGS

app = FastAPI()

def load_json(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
def start():
    return {"status": "API is actief"}

@app.head("/")
def head_root():
    return Response(status_code=200)

@app.get("/search")
def search_endpoint(onderwerp: str = Query(..., description="Het onderwerp om op te zoeken")):
    # Laad de zoekresultaten-configuratie uit ZoekenInternet.json
    try:
        with open("ZoekenInternet.json", encoding="utf-8") as f:
            bronnen = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="ZoekenInternet.json bestand niet gevonden.")
    
    zoekresultaten = bronnen.get(onderwerp, [])
    if not zoekresultaten:
        raise HTTPException(status_code=404, detail=f"Geen zoekresultaten gevonden voor onderwerp: {onderwerp}")

    resultaten = []
    with DDGS() as ddgs:
        for item in zoekresultaten:
            term = item.get("sourceTitle", "") + " " + item.get("description", "")
            for r in ddgs.text(term, max_results=3):
                resultaat = {
                    "titel": r.get("title"),
                    "link": r.get("href"),
                    "samenvatting": r.get("body")
                }
                resultaten.append(resultaat)
    if not resultaten:
        raise HTTPException(status_code=404, detail="Geen relevante updates gevonden.")
    
    # Filter resultaten op geldigheid
    from zoekfilters import filter_resultaten
    gefilterde_resultaten = filter_resultaten(resultaten)
    
    return gefilterde_resultaten[:10]

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
