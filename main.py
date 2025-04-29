# main.py
# Versie: 1.2.1 – bijgewerkt 30 april 2025
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Backend‑API voor GPT Vluchtelingenwerk.

Wijzigingen v1.2.1
------------------
* Nieuwe endpoint **/set_reminder** koppelt reminders aan *afspraakdatum* + *initialen VWN‑medewerker* (geen persoonsgegevens).
* Link‑validatie toegevoegd in `/search`.
* OpenAPI‑spec geüpdatet naar v1.2.1.
* Verder identiek aan v1.2.0 (directory‑agnostische JSON‑loader, /startmenu, /uiflow, enz.).

"""

import json
import logging
import os
from datetime import datetime, timedelta
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

def _validate_link(link: str) -> str:
    """Zorg dat link met http(s) begint. Gooi 500 bij onvolledige link."""
    if not link.startswith(("http://", "https://")):
        logger.error("Onvolledige of relatieve link gevonden: %s", link)
        raise HTTPException(status_code=500, detail="Onvolledige link in bronlijst")
    return link


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
                # rudimentaire filter
                haystack = (item.get("description", "") + " " + item.get("sourceTitle", "")).lower()
                if all(f in haystack or f == "" for f in filters):
                    try:
                        url = _validate_link(item["url"])
                    except HTTPException:
                        # sla ongeldige link over maar log
                        continue
                    results.append(
                        {
                            "titel": item["sourceTitle"],
                            "link": url,
                            "samenvatting": item.get("description", ""),
                            "categorie": categorie,
                        }
                    )
    if not results:
        logger.info("Geen resultaten voor onderwerp '%s'", onderwerp)
    return results


@app.post("/set_reminder")
def set_reminder(
    afspraak_datetime_iso: str,
    medewerker_initialen: str,
    onderwerp: str = "BNTB-check"
) -> Dict[str, Any]:
    """Plan een reminder gekoppeld aan afspraakdatum + initialen.

    Parameters
    ----------
    afspraak_datetime_iso : str
        Afspraakdatum en -tijd in ISO 8601 (bv. 2025-05-15T14:30).
    medewerker_initialen : str
        Initialen van de VWN-medewerker (max. 6 tekens).
    onderwerp : str
        Omschrijving reminder. Standaard 'BNTB-check'.

    Retourneert reminder‑id en geplande uitvoerdatum (afspraak + 28 dagen).
    """
    try:
        afspraak_dt = datetime.fromisoformat(afspraak_datetime_iso)
    except ValueError:
        raise HTTPException(400, detail="ongeldige ISO-datumtijd")

    if not medewerker_initialen or len(medewerker_initialen) > 6:
        raise HTTPException(400, detail="initialen ongeldig")

    run_dt = afspraak_dt + timedelta(days=28)
    reminder_id = f"{onderwerp}-{afspraak_dt.date()}-{medewerker_initialen}"

    # In een echte productie-omgeving zou hier een taak in een queue of DB worden gezet.
    # Voor nu loggen we alleen:
    logger.info("Reminder aangemaakt: %s → %s", reminder_id, run_dt.isoformat())

    return {"reminder_id": reminder_id, "execute_at": run_dt.isoformat()}


@app.get("/generate_image")
def generate_image(prompt: str) -> Dict[str, str]:
    """(Nog) niet geïmplementeerd – placeholder."""
    raise HTTPException(status
