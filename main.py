# main.py
# Versie: 1.2.2 – bijgewerkt 30 april 2025
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backend‑API voor GPT Vluchtelingenwerk.

Wijzigingen v1.2.2
------------------
* `/set_reminder` accepteert nu òf één ISO‑string (`afspraak_datetime_iso`) óf aparte velden `afspraak_datum` + `afspraak_tijd`.
* Overige routes gelijk aan v1.2.1.
"""
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Body

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "GPT vluchtelingenwerk Frontend"
JSON_DIRS = [BACKEND_DIR, FRONTEND_DIR, Path(".").resolve()]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vluchtelingenwerk-backend")
app = FastAPI(title="Vluchtelingenwerk GPT API", version="1.2.2")

# ---------- Helpers ----------

def _find_file(file_name: str) -> Optional[Path]:
    for directory in JSON_DIRS:
        p = directory / file_name
        if p.is_file():
            return p
    return None

def load_json_config(file_name: str) -> Any:
    p = _find_file(file_name)
    if not p:
        raise HTTPException(404, detail=f"{file_name} niet gevonden")
    return json.loads(p.read_text(encoding="utf-8"))

def _validate_link(link: str) -> str:
    if not link.startswith(("http://", "https://")):
        raise HTTPException(500, detail="Onvolledige link in bronlijst")
    return link

# ---------- Routes ----------

@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "API is actief", "version": app.version}

@app.get("/all_procedures")
def get_all_procedures() -> Any:
    return load_json_config("AllProcedures.json")

@app.get("/startmenu")
def get_startmenu() -> Dict[str, Any]:
    uiflow = load_json_config("UIFlow.json")
    for step in uiflow.get("flow", []):
        if step.get("stepId") in ("hoofdmenu", "startmenu"):
            return step
    raise HTTPException(500, detail="Hoofdmenu niet gevonden")

@app.get("/uiflow")
def get_uiflow() -> Any:
    return load_json_config("UIFlow.json")

@app.get("/search")
def search_endpoint(
    onderwerp: str,
    gemeente: str = "",
    thuisland: str = "",
    moedertaal: str = "",
) -> List[Dict[str, Any]]:
    bronnen = load_json_config("ZoekenInternet.json")
    results = []
    filters = (gemeente.lower(), thuisland.lower(), moedertaal.lower())
    for categorie, items in bronnen.items():
        if categorie == "version":
            continue
        for item in items:
            if onderwerp.lower() in (item.get("sourceTitle", "") + item.get("description", "")).lower():
                haystack = (item.get("description", "") + " " + item.get("sourceTitle", "")).lower()
                if all(f in haystack or f == "" for f in filters):
                    url = _validate_link(item["url"])
                    results.append({
                        "titel": item["sourceTitle"],
                        "link": url,
                        "samenvatting": item.get("description", ""),
                        "categorie": categorie,
                    })
    return results

@app.post("/set_reminder")
def set_reminder(
    afspraak_datetime_iso: Optional[str] = Body(default=None),
    afspraak_datum: Optional[str] = Body(default=None),
    afspraak_tijd: Optional[str] = Body(default=None),
    medewerker_initialen: str = Body(..., max_length=6),
    onderwerp: str = Body(default="BNTB-check"),
) -> Dict[str, Any]:
    if afspraak_datetime_iso:
        try:
            afspraak_dt = datetime.fromisoformat(afspraak_datetime_iso)
        except ValueError:
            raise HTTPException(400, detail="afspraak_datetime_iso ongeldig")
    else:
        if not (afspraak_datum and afspraak_tijd):
            raise HTTPException(400, detail="Ontbrekende datum of tijd")
        try:
            afspraak_dt = datetime.fromisoformat(f"{afspraak_datum}T{afspraak_tijd}:00")
        except ValueError:
            raise HTTPException(400, detail="afspraak_datum/tijd ongeldig")

    run_dt = afspraak_dt + timedelta(days=28)
    reminder_id = f"{onderwerp}-{afspraak_dt.date()}-{medewerker_initialen.upper()}"
    logger.info("Reminder aangemaakt: %s → %s", reminder_id, run_dt.isoformat())
    return {"reminder_id": reminder_id, "execute_at": run_dt.isoformat()}

@app.get("/generate_image")
def generate_image(prompt: str):
    raise HTTPException(501, detail="Beeldgeneratie niet geïmplementeerd")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
