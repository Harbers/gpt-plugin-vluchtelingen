# main.py
# Versie: 1.1.0 – bijgewerkt april 2025

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
from fastapi import FastAPI, HTTPException
from typing import Any, Dict, List

# Logging configuratie
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vluchtelingenwerk GPT API", version="1.1.0")

def load_json_config(file_path: str) -> Any:
    """
    Laadt een JSON-configuratiebestand. Geeft een HTTPException bij fouten.
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

@app.get("/all_procedures")
def get_all_procedures() -> Any:
    """
    Retourneert het volledige configuratiebestand met alle juridische procedures.
    """
    return load_json_config("AllProcedures.json")

@app.get("/search")
def search_endpoint(
    onderwerp: str,
    gemeente: str,
    thuisland: str,
    moedertaal: str
) -> List[Dict[str, Any]]:
    """
    Zoekt actuele informatie door de parameters te combineren.
    """
    zoekterm = f"{onderwerp} {gemeente} {thuisland} {moedertaal} samenwerking 10km"
    logger.info(f"Uitgevoerde zoekterm: {zoekterm}")
    # Hier zou een echte zoekfunctie komen; we simuleren een voorbeeldresultaat:
    return [
        {
            "titel": f"Update over {onderwerp} in {gemeente}",
            "link": "https://voorbeeld.nl/update",
            "samenvatting": "Samenvatting van de meest recente ontwikkelingen en regionale initiatieven.",
            "apa": "Voorbeeld, A. (2025). Update over procedures."
        }
    ]

@app.get("/generate_image")
def generate_image(prompt: str) -> Any:
    """
    Proxy naar externe beeldgeneratie‑service (nog niet geïmplementeerd).
    """
    raise HTTPException(status_code=501, detail="Beeldgeneratie nog niet geïmplementeerd")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
