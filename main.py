#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Response, HTTPException, Query
import json
import os
from duckduckgo_search import ddg  # Gebruik de ddg functie in plaats van DDGS

app = FastAPI()

def load_json(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
def start():
    return {"status": "API is active"}

@app.head("/")
def head_root():
    return Response(status_code=200)

@app.get("/search")
def search_endpoint(onderwerp: str = Query(..., description="The subject to search for")):
    # Laad de zoektermen uit het JSON-bestand
    try:
        with open("ZoekenInternet.json", encoding="utf-8") as f:
            bronnen = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="ZoekenInternet.json file not found.")

    zoektermen = bronnen.get(onderwerp, [])
    if not zoektermen:
        raise HTTPException(status_code=404, detail=f"No search terms found for subject: {onderwerp}")

    resultaten = []
    # Voor elke zoekterm worden resultaten opgehaald met de ddg-functie
    for term in zoektermen:
        search_results = ddg(term, max_results=3)
        if search_results:
            for r in search_results:
                resultaat = {
                    "titel": r.get("title"),
                    "link": r.get("href"),
                    "samenvatting": r.get("body")
                }
                resultaten.append(resultaat)
    if not resultaten:
        raise HTTPException(status_code=404, detail="No relevant updates found.")

    # Filter de resultaten op betrouwbare bronnen en Nederlandse context via zoekfilters.py
    from zoekfilters import filter_resultaten
    gefilterde_resultaten = filter_resultaten(resultaten)
    return gefilterde_resultaten[:10]

@app.get("/startmenu")
def startmenu():
    """
    Retourneert de configuratie uit JuridischeProcedure.json voor het menu.
    """
    try:
        menu = load_json("JuridischeProcedure.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JuridischeProcedure.json file not found.")
    return menu

@app.get("/AllProcedures.json")
def get_all_procedures():
    """
    Retourneert het AllProcedures.json-bestand met alle juridische en maatschappelijke procedures.
    """
    try:
        data = load_json("AllProcedures.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="AllProcedures.json file not found.")
    return data

@app.get("/MBInstrumentInvullen.json")
def get_mb_instrument():
    """
    Retourneert het MBInstrumentInvullen.json-bestand met alle vragen, hulplinks, voorlichting en acties.
    """
    try:
        data = load_json("MBInstrumentInvullen.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="MBInstrumentInvullen.json file not found.")
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
