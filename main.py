#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Response, HTTPException, Query, Request
import json
import os
from duckduckgo_search import DDGS

app = FastAPI()

# Middleware voor IP-whitelisting
ALLOWED_IPS = {"18.156.158.53", "18.156.42.200", "52.59.103.54"}

@app.middleware("http")
async def ip_whitelist_middleware(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="Access forbidden: IP not allowed")
    response = await call_next(request)
    return response

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
