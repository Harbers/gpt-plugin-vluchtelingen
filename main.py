#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Response, HTTPException, Query
import json
import os
from duckduckgo_search import DDGS

app = FastAPI(
    title="GPT Plugin Vluchtelingenwerk API",
    description="API voor het digitale begeleidings- en juridische informatie-instrument",
    version="1.0"
)

def load_json(file_path: str):
    """Laadt een JSON-bestand en retourneert de inhoud."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Basis endpoints

@app.get("/", summary="API Status", response_description="API is actief")
def root():
    return {"status": "API is actief"}

@app.head("/")
def head_root():
    return Response(status_code=200)

# Zoekfunctionaliteit

@app.get("/search", summary="Zoek op onderwerp")
def search_endpoint(onderwerp: str = Query(..., description="Het onderwerp om op te zoeken")):
    """
    Haalt zoektermen op uit ZoekenInternet.json en voert een DuckDuckGo-zoekopdracht uit.
    """
    try:
        with open("ZoekenInternet.json", encoding="utf-8") as f:
            bronnen = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="ZoekenInternet.json bestand niet gevonden.")
    
    zoektermen = bronnen.get(onderwerp, [])
    if not zoektermen:
        raise HTTPException(status_code=404, detail=f"Geen zoektermen gevonden voor onderwerp: {onderwerp}")
    
    resultaten = []
    with DDGS() as ddgs:
        for term in zoektermen:
            for r in ddgs.text(term, max_results=3):
                resultaat = {
                    "titel": r.get("title"),
                    "link": r.get("href"),
                    "samenvatting": r.get("body")
                }
                resultaten.append(resultaat)
    if not resultaten:
        raise HTTPException(status_code=404, detail="Geen relevante updates gevonden.")
    return resultaten[:10]

# Configuratie endpoints

@app.get("/startmenu", summary="Laad startmenu configuratie")
def startmenu():
    """
    Laadt de configuratie uit JuridischeProcedure.json voor het starten van het menu.
    """
    try:
        menu = load_json("JuridischeProcedure.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JuridischeProcedure.json bestand niet gevonden.")
    return menu

# Endpoints voor het beschikbaar stellen van de JSON-bestanden

@app.get("/AllProcedures.json", summary="Laad alle procedures")
def get_all_procedures():
    """
    Retourneert het AllProcedures.json-bestand.
    """
    try:
        data = load_json("AllProcedures.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="AllProcedures.json bestand niet gevonden.")
    return data

@app.get("/UIFlow.json", summary="Laad de UI-flow")
def get_ui_flow():
    """
    Retourneert het UIFlow.json-bestand.
    """
    try:
        data = load_json("UIFlow.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="UIFlow.json bestand niet gevonden.")
    return data

@app.get("/MBInstrumentInvullen.json", summary="Laad MB Instrument data")
def get_mb_instrument():
    """
    Retourneert het MBInstrumentInvullen.json-bestand.
    """
    try:
        data = load_json("MBInstrumentInvullen.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="MBInstrumentInvullen.json bestand niet gevonden.")
    return data
