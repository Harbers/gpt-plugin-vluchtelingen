# main.py
# Versie: 1.2.0 – bijgewerkt 30 april 2025
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Backend‑API voor GPT Vluchtelingenwerk.

Wijzigingen v1.2.1
------------------
* Directory‑agnostische JSON‑loader zodat bestanden uit de frontend‑map direct gebruikt kunnen worden
* Nieuwe endpoints: /startmenu, /uiflow **en /set_reminder**
* /all_procedures gebruikt nieuwe loader
* /search zoekt nu in lokale JSON‑bronnen i.p.v. dummy‑data
* **/set_reminder** koppelt reminders aan afspraak‑datum + initialen medewerker, geen V‑nummer nodig
* OpenAPI‑spec geüpdatet naar v1.2.1 (zie openapi.yaml)
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException

# ------------ Configuratie --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "GPT vluchtelingenwerk Frontend"

JSON_DIRS = [
    BACKEND_DIR,
    FRONTEND_DIR,
    Path(".").resolve(),  # fallback: werkdirectory van runtime
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vluchtelingenwerk-backend")

app = FastAPI(title="Vluchtelingenwerk GPT API", version="1.2.1")


# ------------ Hulpfuncties --------------------------------------------------

def _find_file(file_name: str) -> Optional[Path]:
    """Zoek `file_name` in `JSON_DIRS`. Retourneer Path of None."""
    for directory in JSON_DIRS:
        candidate = directory / file_name
        if candidate.is_file():
            return candidate
    return None


def load_json_config(file_name: str) -> Any:
    """Laad JSON‑bestand ongeacht locatie (backend/frontend)."""
    path = _find_file(file_name)
    if not path:
        logger.error("Bestand %s niet gevonden in %s", file_name, JSON_DIRS)
        raise HTTPException(status_code=404, detail=f"{file_name} niet gevonden")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.exception("Fout bij laden van %s: %s", file_name, exc)
        raise HTTPException(status_code=500, detail=f"Fout bij laden van {file_name}")


# ------------ API‑routes ----------------------------------------------------

@app.get("/")
def root() -> Dict[str, str]:
    """Health‑check endpoint."""
    return {"status": "API is actief", "version": app.version}


@app.get("/all_procedures")
def get_all_procedures() -> Any:
    """Volledige set procedures voor juristen / front‑end."""
    return load_json_config("AllProcedures.json")


@app.get("/startmenu")
def get_startmenu() -> Dict[str, Any]:
    """Levert het hoofdmenu uit UIFlow.json (stepId == 'hoofdmenu')."""
    uiflow = load_json_config("UIFlow.json")
    for step in uiflow.get("flow", []):
        if step.get("stepId") in ("hoofdmenu", "startmenu"):
            return step
    raise HTTPException(status_code=500, detail="Hoofdmenu niet gevonden in UIFlow.json")


@app.get("/uiflow")
def get_uiflow() -> Any:
    """Geeft het complete UI‑flow JSON terug."""
    return load_json_config("UIFlow.json")


@app.get("/search")
def search_endpoint(
    onderwerp: str,
    gemeente: str = "",
    thuisland: str = "",
    moedertaal: str = "",
) -> List[Dict[str, Any]]:
    """Zoek in lokale bronlijst ZoekenInternet.json op onderwerp + filters."""
    bronnen = load_json_config("ZoekenInternet.json")
    results = []
    filters = (gemeente.lower(), thuisland.lower(), moedertaal.lower())
    for categorie, items in bronnen.items():
        if categorie == "version":
            continue
        for item in items:
            titel_match = onderwerp.lower() in item.get("sourceTitle", "").lower()
            desc_match = onderwerp.lower() in item.get("description", "").lower()
            if titel_match or desc_match:
                haystack = (item.get("description", "") + " " + item.get("sourceTitle", "")).lower()
                if all(f in haystack or f == "" for f in filters):
                    results.append(
                        {
                            "titel": item["sourceTitle"],
                            "link": item["url"],
                            "samenvatting": item.get("description", ""),
                            "categorie": categorie,
                        }
                    )
    return results


# ---------------- Reminder --------------------------------------------------
from pydantic import BaseModel, validator
from datetime import datetime, timedelta

class ReminderRequest(BaseModel):
    appointment_datetime: datetime
    initials: str
    days_until_alert: int = 28
    description: str

    @validator("initials")
    def validate_initials(cls, v):
        v = v.strip().upper()
        if not (1 <= len(v) <= 6):
            raise ValueError("initials must be 1‑6 characters")
        return v

@app.post("/set_reminder")
def set_reminder(req: ReminderRequest):
    """Zet een reminder gekoppeld aan afspraak‑datum en initialen."""
    trigger_at = req.appointment_datetime + timedelta(days=req.days_until_alert)
    title = f"BNTB-check {req.appointment_datetime.date()} {req.initials}"
    # Hier zou een echte automation‑service worden aangeroepen; placeholder‑response:
    logger.info("Reminder gepland: %s op %s", title, trigger_at.isoformat())
    return {"status": "scheduled", "title": title, "trigger_at": trigger_at}


@app.get("/generate_image")
def generate_image(prompt: str) -> Dict[str, str]:
    """(Nog) niet geïmplementeerd – placeholder."""
    raise HTTPException(status_code=501, detail="Beeldgeneratie nog niet geïmplementeerd")


# ------------ Local dev -----------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
