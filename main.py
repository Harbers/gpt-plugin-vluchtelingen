#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import logging
import requests
from fastapi import FastAPI, HTTPException, Query, Response
from typing import Any, Dict, List

# Logging configuratie
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vluchtelingenwerk GPT API", version="1.0.0")

def load_json_config(file_path: str) -> Any:
    """
    Laadt een JSON-configuratiebestand.
    """
    if not os.path.isfile(file_path):
        logger.error(f"Bestand {file_path} niet gevonden.")
        raise HTTPException(status_code=404, detail=f"{file_path} niet gevonden.")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fout bij het laden van {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Fout bij het laden van {file_path}")

@app.get("/")
def root() -> Dict[str, str]:
    """
    Basis endpoint om te controleren of de API actief is.
    """
    return {"status": "API is actief"}

@app.head("/")
def head_root() -> Response:
    """
    HEAD-endpoint om te controleren of de API bereikbaar is.
    """
    return Response(status_code=200)

@app.get("/all_procedures")
def get_all_procedures() -> Any:
    """
    Endpoint dat het complete configuratiebestand met alle procedures retourneert.
    Dit bestand wordt gebruikt als gemeenschappelijke configuratie voor zowel de backend als de frontend.
    """
    return load_json_config("AllProcedures.json")

@app.get("/generate_image")
def generate_image(prompt: str = Query(..., description="Prompt voor beeldgeneratie")) -> Any:
    """
    Endpoint voor externe beeldgeneratie.
    Pas deze functie aan volgens de specificaties van uw gekozen externe API voor beeldgeneratie.
    """
    api_url = "https://externe-api-beeldgeneratie.nl/generate"  # Pas deze URL aan
    try:
        response = requests.post(api_url, json={"prompt": prompt})
        if response.status_code != 200:
            logger.error("Fout bij beeldgeneratie: " + response.text)
            raise HTTPException(status_code=500, detail="Fout bij beeldgeneratie")
        return response.json()
    except Exception as e:
        logger.error(f"Fout bij de API-call voor beeldgeneratie: {e}")
        raise HTTPException(status_code=500, detail="Fout bij beeldgeneratie")

@app.get("/mb_instrument")
def get_mb_instrument() -> Any:
    """
    Endpoint om de configuratie voor het MB‑Instrument op te halen.
    """
    return load_json_config("MBInstrumentInvullen.json")

@app.get("/search")
def search_endpoint(
    onderwerp: str = Query(..., description="Onderwerp om op te zoeken"),
    gemeente: str = Query(..., description="Ingevoerde gemeente"),
    thuisland: str = Query(..., description="Ingevoerde thuisland"),
    moedertaal: str = Query(..., description="Ingevoerde moedertaal")
) -> List[Dict[str, Any]]:
    """
    Voert een internetzoekopdracht uit door het onderwerp te combineren met de ingevoerde basisgegevens (gemeente, thuisland en moedertaal).
    Deze zoekopdracht is bedoeld om beter afgestemde resultaten te verkrijgen, inclusief regionale samenwerkingsinitiatieven binnen 10 km.
    
    In een echte implementatie wordt hier een call gedaan naar een zoekmachine of een externe API.
    """
    # Combineer de basisgegevens met het onderwerp voor een samengestelde zoekterm.
    zoekterm = f"{onderwerp} {gemeente} {thuisland} {moedertaal} samenwerking 10km"
    logger.info(f"Uitgevoerde zoekterm: {zoekterm}")
    
    # Simuleer een zoekopdracht – pas dit aan naar een echte zoekfunctie.
    dummy_resultaten = [
        {
            "titel": f"Update over {onderwerp} in {gemeente}",
            "link": "https://voorbeeld.nl/update",
            "samenvatting": "Samenvatting van de meest recente ontwikkelingen en regionale initiatieven."
        }
    ]
    return dummy_resultaten

# Hier kunnen extra endpoints worden toegevoegd voor aanvullende functionaliteiten

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
