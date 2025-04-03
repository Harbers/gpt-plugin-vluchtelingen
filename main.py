#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py - Backend voor DuckDuckGo-zoekfunctionaliteit

Deze FastAPI-applicatie verzorgt uitsluitend de zoekfunctie. Op basis van een meegegeven onderwerp
wordt in het bestand 'ZoekenInternet.json' gezocht naar relevante zoektermen.
Voor iedere zoekterm wordt met behulp van de duckduckgo_search module actuele informatie opgehaald.
De resultaten worden, na filtering en anonimisering, als JSON teruggegeven.

Deze backend is gehost op:
    https://gpt-plugin-vluchtelingen.onrender.com

Alle procedurele stappen (menu’s, vragen, handelingsplannen, etc.) worden volledig door de frontend afgehandeld.
De backend fungeert uitsluitend als zoekmachine-brug.

De API-documentatie is beschikbaar via Redoc op: /redoc
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Response
import json
import os
from duckduckgo_search import ddg  # Gebruik de ddg functie voor zoeken
from zoekfilters import filter_resultaten  # Import filtering en anonimisatiefuncties

app = FastAPI(
    title="Vluchtelingen Zoekplugin API",
    description="Backend voor het ophalen van actuele informatie via DuckDuckGo. Gehost op https://gpt-plugin-vluchtelingen.onrender.com",
    version="1.0.0",
    docs_url=None,       # Swagger UI uitschakelen
    redoc_url="/redoc"   # Redoc-documentatie beschikbaar op /redoc
)

def load_json(file_path: str) -> dict:
    """
    Laadt een JSON-bestand met de gegeven file path en retourneert een dictionary.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Mapping van gebruikersvriendelijke termen naar de sleutels in ZoekenInternet.json
SUBJECT_MAPPING = {
    "Asielprocedure": "Asielbeleid en Wetgeving",
    "Dublin": "Jurisprudentie en Rechtspraak"
    # Voeg hier meer mappings toe indien gewenst
}

@app.get("/", summary="Controleer of de API actief is")
def root():
    """
    Basis-endpoint om te controleren of de API actief is.
    """
    return {"status": "API is actief"}

@app.head("/", summary="HEAD-request voor health-check")
def head_root():
    """
    Eenvoudige HEAD-endpoint om een 200 OK response terug te geven.
    """
    return Response(status_code=200)

@app.get("/search", summary="Zoek actuele informatie via DuckDuckGo")
def search_endpoint(
    onderwerp: Optional[str] = Query(
        default="Asielprocedure", 
        description="Het onderwerp om op te zoeken (bijv. 'Asielprocedure', 'Dublin', etc.). Laat deze parameter weg of geef niets op om standaard 'Asielprocedure' te gebruiken.",
        required=False
    )
):
    """
    Endpoint voor het ophalen van actuele zoekresultaten via DuckDuckGo.

    Werking:
    1. Laad de zoektermen voor het gegeven onderwerp uit 'ZoekenInternet.json'.
    2. Gebruik een mapping om gebruikersvriendelijke termen te vertalen naar de juiste sleutel in het JSON-bestand.
    3. Voor iedere zoekterm worden maximaal 3 resultaten opgehaald via DuckDuckGo.
    4. De verzamelde resultaten worden vervolgens gefilterd en geanonimiseerd.
    5. De uiteindelijke, veilige resultaten worden als JSON teruggegeven.

    :param onderwerp: De naam van het onderwerp.
    :return: Een lijst met zoekresultaten met titel, link en samenvatting.
    """
    try:
        zoekdata = load_json("ZoekenInternet.json")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Gebruik de mapping om de juiste sleutel te vinden
    sleutel = SUBJECT_MAPPING.get(onderwerp, onderwerp)
    zoektermen = zoekdata.get(sleutel, [])
    if not zoektermen:
        raise HTTPException(status_code=404, detail=f"Geen zoektermen gevonden voor onderwerp: {onderwerp}")

    resultaten = []
    try:
        # Gebruik de ddg-functie om per zoekterm maximaal 3 resultaten op te halen
        for term in zoektermen:
            for result in ddg(term, max_results=3):
                resultaat = {
                    "titel": result.get("title"),
                    "link": result.get("href"),
                    "samenvatting": result.get("body")
                }
                resultaten.append(resultaat)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij het ophalen van zoekresultaten: {e}")

    # Filter de zoekresultaten voor relevante, veilige output
    resultaten = filter_resultaten(resultaten)

    if not resultaten:
        raise HTTPException(status_code=404, detail="Geen relevante resultaten gevonden.")
    
    return resultaten

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
