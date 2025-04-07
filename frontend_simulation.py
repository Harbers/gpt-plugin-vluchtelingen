#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests
from typing import Any, Dict, List

def laad_json(bestandsnaam: str) -> Any:
    pad = os.path.join(os.path.dirname(__file__), bestandsnaam)
    with open(pad, "r", encoding="utf-8") as bestand:
        return json.load(bestand)

def startmenu() -> None:
    print("Welkom bij de begeleidingsassistent voor Vluchtelingenwerk Nederland.")
    print("Let op: Voer uitsluitend anonieme gegevens in over uw cliënt (geen namen, BSN-nummers of V‑nummers).")
    print("Kies een optie:")
    print("1. Ik ben juridisch begeleider.")
    print("2. Juridische casus behandelen.")
    print("3. Ik ben maatschappelijk begeleider.")
    print("4. Maatschappelijke casus behandelen.")
    
    keuze = input("Maak uw keuze (1-4): ").strip()
    if keuze == "1":
        optie_juridisch_begeleider()
    elif keuze == "2":
        optie_juridische_casus()
    elif keuze == "3":
        optie_maatschappelijk_begeleider()
    elif keuze == "4":
        optie_maatschappelijke_casus()
    else:
        print("Ongeldige keuze. Probeer het opnieuw.")
        startmenu()

def optie_juridisch_begeleider() -> None:
    procedures = laad_json("AllProcedures.json")
    print("U heeft gekozen voor: Juridisch begeleider.")
    print("Beschikbare onderwerpen:")
    juridische_subjects: List[Dict[str, Any]] = procedures.get("juridischeProcedures", [])
    for idx, proc in enumerate(juridische_subjects, start=1):
        print(f"{idx}. {proc.get('title', 'Onbekend')}")
    keuze = input("Voer het nummer in van het gewenste onderwerp: ").strip()
    try:
        idx = int(keuze) - 1
        geselecteerd = juridische_subjects[idx]
        print(f"U heeft gekozen: {geselecteerd.get('title')}")
        resultaten = doe_zoekopdracht(geselecteerd.get("title"))
        toon_resultaten(resultaten)
    except (IndexError, ValueError):
        print("Ongeldige keuze.")
        optie_juridisch_begeleider()

def optie_juridische_casus() -> None:
    print("U heeft gekozen voor: Juridische casus behandelen.")
    print("Let op: Gebruik uitsluitend anonieme gegevens.")
    casusinfo: Dict[str, str] = {}
    casusinfo["kern"] = input("Wat is de aanleiding van de casus? ").strip()
    casusinfo["documenten"] = input("Welke documenten zijn betrokken? ").strip()
    casusinfo["belang"] = input("Wat is het belang van uw cliënt? ").strip()
    casusinfo["termijnen"] = input("Zijn er belangrijke termijnen? ").strip()
    print("Actuele juridische informatie wordt opgezocht...")
    resultaten = doe_zoekopdracht(casusinfo["kern"])
    toon_resultaten(resultaten)
    indien_plan = input("Is de informatie voldoende of wilt u een handelingsplan? (ja/nee): ").strip().lower()
    if indien_plan == "ja":
        print("Er wordt een juridisch handelingsplan opgesteld met SMART-doelen.")

def optie_maatschappelijk_begeleider() -> None:
    uitleg = laad_json("AlgemeneInstructies.json")
    print("U heeft gekozen voor: Maatschappelijk begeleider.")
    print(uitleg.get("algemeneInstructies", {}).get("title", "Geen uitleg beschikbaar."))
    input("Druk op Enter om het MB‑Instrument te starten...")
    # Hier zou het MB‑Instrument worden gestart (apart scriptbestand)

def optie_maatschappelijke_casus() -> None:
    print("U heeft gekozen voor: Maatschappelijke casus behandelen.")
    print("Let op: Gebruik uitsluitend anonieme gegevens.")
    gemeente = input("In welke gemeente woont uw cliënt? ").strip()
    taal = input("Wat is de moedertaal van uw cliënt? (en/ar/tr/fa/fr/pr/so/ti/nl): ").strip().lower()
    casusinfo: Dict[str, str] = {}
    casusinfo["algemeen"] = input("Wat is de algemene aanleiding van de situatie? ").strip()
    thema = "Financiën"  # Voorbeeldthema
    print(f"Het gekozen thema is: {thema}")
    vervolgvragen = [
        "Beschrijf de huidige situatie van uw cliënt op dit gebied.",
        "Zijn er al instanties betrokken?",
        "Wat waren concrete zorgen?",
        "Wat zijn de belangrijkste zorgen?",
        "Wat is een mogelijke eerste stap?"
    ]
    for vraag in vervolgvragen:
        input(f"{vraag} ")
    print("Online informatie wordt opgezocht...")
    resultaten = doe_zoekopdracht(f"{thema} hulp {gemeente}")
    toon_resultaten(resultaten)
    plan = input("Is de informatie voldoende of wilt u een handelingsplan? (ja/nee): ").strip().lower()
    if plan == "ja":
        print(f"Er wordt een handelingsplan opgesteld met SMART-doelen. Bijvoorbeeld: Binnen 7 dagen contact met Schuldhulpverlening van {gemeente}.")

def doe_zoekopdracht(onderwerp: str) -> List[Dict[str, str]]:
    try:
        response = requests.get("https://gpt-plugin-vluchtelingen.onrender.com/search", params={"onderwerp": onderwerp})
        if response.status_code == 200:
            return response.json()
        else:
            print("Geen resultaten gevonden.")
            return []
    except Exception as e:
        print(f"Fout bij zoekopdracht: {e}")
        return []

def toon_resultaten(resultaten: List[Dict[str, str]]) -> None:
    if not resultaten:
        print("Geen resultaten gevonden.")
        return
    print("Resultaten:")
    for res in resultaten:
        print(f" - {res.get('titel', 'Geen titel')}")
        print(f"   Link: {res.get('link', 'Geen link')}")
        print(f"   Samenvatting: {res.get('samenvatting', 'Geen samenvatting')}\n")

if __name__ == "__main__":
    startmenu()
