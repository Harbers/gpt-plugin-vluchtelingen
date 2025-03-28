#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests
from bs4 import BeautifulSoup
import feedparser  # pip install feedparser
from datetime import datetime, timedelta
from urllib.parse import quote
from duckduckgo_search import ddg  # pip install duckduckgo_search

def load_json(file_path):
    from duckduckgo_search import ddg  # pip install duckduckgo_search
from fastapi import FastAPI  # ✅ voeg deze regel toe

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def ask_question(question):
    nummer = question["nummer"]
    tekst = question["tekst"]
    antwoord_opties = question["antwoordOpties"]
    print(f"\nVraag {nummer}: {tekst}")
    print("Kies uit de volgende opties:")
    for i, optie in enumerate(antwoord_opties, start=1):
        print(f"{i}. {optie}")
    valid_inputs = ["1", "2", "3", "4", "NVT"]
    user_input = input("Voer het nummer (1,2,3,4) of 'NVT' in: ").strip().upper()
    while user_input not in valid_inputs:
        print("Ongeldige keuze. Probeer opnieuw.")
        user_input = input("Voer het nummer (1,2,3,4) of 'NVT' in: ").strip().upper()
    if user_input == "NVT":
        chosen_answer = antwoord_opties[-1]
    else:
        idx = int(user_input) - 1
        chosen_answer = antwoord_opties[idx]
    if user_input in ["1", "2"] and "linksVoorlichting" in question and question["linksVoorlichting"]:
        print("\n=== RELEVANTE VOORLICHTING EN ACTIES ===")
        for link in question["linksVoorlichting"]:
            print(f" - {link}")
    return chosen_answer

def show_juridische_onderwerpen(juridische_data):
    topics = juridische_data.get("onderwerpen", [])
    n = len(topics)
    half = (n + 1) // 2
    print("\nKies een onderwerp uit onderstaande lijst van 20 juridische thema’s. Geef het nummer in van het gewenste onderwerp:")
    for i in range(half):
        left_num = i + 1
        left_topic = topics[i]["title"] if i < n else ""
        right_index = i + half
        if right_index < n:
            right_num = right_index + 1
            right_topic = topics[right_index]["title"]
        else:
            right_num = ""
            right_topic = ""
        print(f"{left_num:>2}. {left_topic:<40}   {right_num:>2}. {right_topic}")
    keuze = input("\nTyp het nummer van het onderwerp waarin u juridische informatie zoekt: ").strip()
    return keuze

def fetch_latest_updates(rss_url, max_items=10, section="Recente ontwikkelingen (RSS)"):
    print(f"\n=== {section} ===")
    feed = feedparser.parse(rss_url)
    if feed.bozo:
        print("Fout bij het ophalen van de RSS-feed.")
        return
    now = datetime.now()
    twelve_months_ago = now - timedelta(days=365)
    filtered_entries = []
    for entry in feed.entries:
        if 'published_parsed' in entry and entry.published_parsed:
            published_dt = datetime(*entry.published_parsed[:6])
            if published_dt >= twelve_months_ago:
                filtered_entries.append((published_dt, entry))
    filtered_entries.sort(key=lambda x: x[0], reverse=True)
    filtered_entries = filtered_entries[:max_items]
    if not filtered_entries:
        print("Geen recente ontwikkelingen gevonden in de afgelopen 12 maanden via RSS.")
        return
    for pub_date, entry in filtered_entries:
        title = entry.get("title", "Geen titel")
        published = entry.get("published", pub_date.strftime("%Y-%m-%d"))
        summary = entry.get("summary", "Geen samenvatting beschikbaar.")
        link = entry.get("link", "")
        print(f"- {title} ({published})")
        print(f"  {summary}")
        print(f"  Lees meer: {link}")

def search_plugin_updates(subject, max_items=10, section="Externe zoekresultaten (Plugin)"):
    """
    Voert een zoekopdracht uit met behulp van de ingebouwde zoekplugin van ChatGPT.
    Er wordt gezocht op de zoektermen zoals gedefinieerd in 'externeZoekactie' van het onderwerp.
    """
    print(f"\n=== {section} ===")
    zoekTermen = subject.get("externeZoekactie", {}).get("zoekTermen", [])
    if not zoekTermen:
        print("Geen zoektermen beschikbaar voor externe zoekacties.")
        return
    all_results = []
    for term in zoekTermen:
        results = search_with_plugin(term, max_items)
        all_results.extend(results)
        if len(all_results) >= max_items:
            break
    all_results = all_results[:max_items]
    if not all_results:
        print("Geen externe zoekresultaten gevonden via de ingebouwde plugin.")
    else:
        for item in all_results:
            print(f"- {item['title']} ({item['published']})")
            print(f"  {item['summary']}")
            print(f"  Lees meer: {item['link']}")

def search_duckduckgo_free(subject, max_items=10, section="Externe zoekresultaten (DuckDuckGo)"):
    """
    Voert een gratis zoekopdracht uit met behulp van de module duckduckgo_search.
    Er wordt gezocht op de zoektermen uit het veld 'externeZoekactie' van het onderwerp.
    """
    print(f"\n=== {section} ===")
    zoekTermen = subject.get("externeZoekactie", {}).get("zoekTermen", [])
    if not zoekTermen:
        print("Geen zoektermen beschikbaar voor externe zoekacties.")
        return
    results = []
    for term in zoekTermen:
        try:
            for result in ddg(term, max_results=max_items):
                title = result.get("title", "Geen titel")
                link = result.get("href", "")
                summary = result.get("body", "Samenvatting niet beschikbaar.")
                published = datetime.now().strftime("%Y-%m-%d")
                results.append({"title": title, "published": published, "link": link, "summary": summary})
                if len(results) >= max_items:
                    break
            if len(results) >= max_items:
                break
        except Exception as e:
            print(f"Fout bij DuckDuckGo zoekactie voor term '{term}': {str(e)}")
        if len(results) >= max_items:
            break
    if not results:
        print("Geen externe zoekresultaten gevonden via DuckDuckGo.")
    else:
        for item in results:
            print(f"- {item['title']} ({item['published']})")
            print(f"  {item['summary']}")
            print(f"  Lees meer: {item['link']}")

def fetch_informatie(onderwerp_nummer, main_data):
    juridische_data = main_data.get("juridischeProcedure", {})
    subject = juridische_data["onderwerpen"][onderwerp_nummer]
    title = subject["title"]
    context = juridische_data.get("context", "")
    if "asiel" not in context.lower():
        return {
            "titel": title,
            "publicatiedatum": "Niet beschikbaar",
            "url": "",
            "samenvatting": "De context van deze informatie is niet primair gericht op asielzoekers."
        }
    if "sources" in subject and subject["sources"]:
        chosen_source = subject["sources"][0]
        url = chosen_source["url"]
    else:
        return {
            "titel": title,
            "publicatiedatum": "Niet beschikbaar",
            "url": "",
            "samenvatting": "Geen bron beschikbaar in de gegevens."
        }
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.get_text(separator=" ", strip=True)[:150]
            pub_date = "Niet beschikbaar"
            if "rss" in url.lower():
                pub_date = "Datum uit RSS-feed"
            return {
                "titel": chosen_source["sourceTitle"],
                "publicatiedatum": pub_date,
                "url": url,
                "samenvatting": content
            }
        else:
            return {
                "titel": chosen_source["sourceTitle"],
                "publicatiedatum": "Niet beschikbaar",
                "url": url,
                "samenvatting": f"Fout bij ophalen: HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "titel": chosen_source["sourceTitle"],
            "publicatiedatum": "Niet beschikbaar",
            "url": url,
            "samenvatting": f"Fout bij ophalen: {str(e)}"
        }

def process_juridische_procedure(main_data, show_startvraag=True):
    # Laad de juridische proceduregegevens
    juridische_data = {}
    if "juridischeProcedure" in main_data:
        jp_section = main_data["juridischeProcedure"]
        if isinstance(jp_section, dict) and "file" in jp_section:
            try:
                juridische_data = load_json(jp_section["file"])
            except FileNotFoundError:
                juridische_data = {}
        else:
            juridische_data = jp_section
    if not juridische_data:
        print("Geen juridische procedure-informatie gevonden.")
        return
    if show_startvraag:
        print(f"\nStartvraag: {juridische_data.get('startVraag')}")
    keuze = show_juridische_onderwerpen(juridische_data)
    try:
        onderwerp_index = int(keuze) - 1
        if onderwerp_index < 0 or onderwerp_index >= len(juridische_data["onderwerpen"]):
            print("Ongeldige keuze.")
            return
    except ValueError:
        print("Ongeldige invoer.")
        return
    onderwerp = juridische_data["onderwerpen"][onderwerp_index]
    gekozen_onderwerp = onderwerp["title"]
    print(f"\nU heeft gekozen voor: {gekozen_onderwerp}")
    
    # Basisinformatie ophalen
    info = fetch_informatie(onderwerp_index, {"juridischeProcedure": juridische_data})
    print("\n=== GEVONDEN INFORMATIE ===")
    print(f"Titel: {info['titel']}")
    print(f"Publicatiedatum: {info['publicatiedatum']}")
    print(f"URL: {info['url']}")
    print(f"Samenvatting: {info['samenvatting']}")
    print("\nBronvermelding volgens APA-standaard:")
    print(f"{info['titel']}. ({info['publicatiedatum']}). Geraadpleegd van {info['url']}")
    
    # Haal RSS-resultaten op
    print("\n=== Recente ontwikkelingen (RSS) ===")
    if "laatsteOntwikkelingen" in onderwerp and "rss" in onderwerp["laatsteOntwikkelingen"]:
        fetch_latest_updates(onderwerp["laatsteOntwikkelingen"]["rss"], max_items=10, section="Recente ontwikkelingen (RSS)")
    else:
        print("Geen RSS-feed beschikbaar voor recente ontwikkelingen.")
    
    # Gebruik de ingebouwde zoekplugin (Plugin) om externe zoekresultaten op te halen
    print("\n=== Externe zoekresultaten (Plugin) ===")
    search_plugin_updates(onderwerp, max_items=10, section="Externe zoekresultaten (Plugin)")
    
    # Gebruik als alternatief DuckDuckGo voor externe zoekresultaten
    print("\n=== Externe zoekresultaten (DuckDuckGo) ===")
    search_duckduckgo_free(onderwerp, max_items=10, section="Externe zoekresultaten (DuckDuckGo)")
    
    # Indien er documenten zijn gekoppeld, toon deze ook
    if "documenten" in onderwerp and "laatsteDocumenten" in onderwerp["documenten"] and "rss" in onderwerp["documenten"]["laatsteDocumenten"]:
        print("\n=== Documenten ===")
        fetch_latest_updates(onderwerp["documenten"]["laatsteDocumenten"]["rss"], max_items=10, section="Documenten")

def start_casusanalyse(main_data):
    print("\nWilt u een juridische casus bespreken? (ja/nee)")
    antwoord = input().strip().lower()
    if antwoord != "ja":
        print("Oké, geen casusanalyse uitgevoerd.")
        return
    print("\nLaten we beginnen met de casusanalyse. Beantwoord alstublieft de volgende juridische vragen.")
    casus_data = {}
    casus_data["aanleiding"] = input("Wat is de juridische aanleiding van de casus? ")
    casus_data["rechtsbelang"] = input("Wat is het juridische belang voor de cliënt? ")
    casus_data["documenten"] = input("Beschrijf kort de relevante documenten of besluiten: ")
    casus_data["termijn"] = input("Is er een specifieke termijn of deadline? ")
    while True:
        extra = input("Zijn er nog andere relevante feiten of juridische aspecten? (typ 'nee' als alles duidelijk is) ")
        if extra.strip().lower() == "nee":
            break
        casus_data.setdefault("andere_feiten", []).append(extra)
    print("\n=== VERZAMELDE CASUSINFORMATIE ===")
    for key, value in casus_data.items():
        print(f"{key}: {value}")
    juridisch_advies = (
        "Op basis van de verstrekte informatie adviseren wij: Controleer het besluit grondig, verzamel alle relevante documenten en overweeg een formeel bezwaar. "
        "Neem contact op met een gespecialiseerde advocaat voor verdere begeleiding."
    )
    print("\n=== JURIDISCH ADVIES ===")
    print(juridisch_advies)
    verslag_keuze = input("\nWilt u deze casus en het juridisch advies in een verslag vastleggen? (ja/nee) ").strip().lower()
    if verslag_keuze == "ja":
        verslag = {
            "casus_data": casus_data,
            "juridisch_advies": juridisch_advies,
            "bronvermelding": "Gebruik de relevante officiële en erkende bronnen (zie juridischeProcedure in main.json)"
        }
        with open("JuridischVerslag.txt", "w", encoding="utf-8") as f:
            f.write("Juridisch Verslag\n")
            f.write("================\n")
            for key, value in verslag["casus_data"].items():
                f.write(f"{key}: {value}\n")
            f.write("\nJuridisch Advies:\n")
            f.write(juridisch_advies + "\n")
            f.write("\nBronvermelding:\n")
            f.write(verslag["bronvermelding"] + "\n")
        print("\nHet verslag is gegenereerd en opgeslagen als 'JuridischVerslag.txt'.")
    else:
        print("Casus en advies worden niet vastgelegd als verslag.")

def start_nareizigers():
    procedures = load_json("procedures.json")
    print("\nWelkom! U heeft gekozen voor de rol 'nareizigers'.")
    print("U kunt de volgende procedures raadplegen:\n")
    for key, proc in procedures.items():
        print(f"{key}: {proc['title']}")
        print(f"   {proc['description']}\n")
    keuze = input("Geef het procodenummer of de titel in (bijv. PROC001 of MVV-aanvraag): ").strip()
    if keuze.upper() in procedures:
        selected_proc = procedures[keuze.upper()]
        print("\n=== PROCEDURE DETAILS ===")
        print(f"Titel: {selected_proc['title']}")
        print(f"Beschrijving: {selected_proc['description']}")
        print("Stappen:")
        for step in selected_proc["steps"]:
            print(f" - Stap {step['step']}: {step['description']}")
    else:
        found = False
        for key, proc in procedures.items():
            if keuze.lower() in proc["title"].lower():
                selected_proc = proc
                found = True
                print("\n=== PROCEDURE DETAILS ===")
                print(f"Titel: {selected_proc['title']}")
                print(f"Beschrijving: {selected_proc['description']}")
                print("Stappen:")
                for step in selected_proc["steps"]:
                    print(f" - Stap {step['step']}: {step['description']}")
                break
        if not found:
            print("Geen geldige keuze gemaakt.")

def start_mb_instrument():
    """
    Start het traject voor Maatschappelijk Begeleider met betrekking tot het invullen van het MB‑Instrument.
    De gebruiker kan kiezen tussen:
      1. Het invullen van het MB‑Instrument (vragen uit de module 'mb_instrument').
      2. Het bekijken van de begeleidende procedure (stapsgewijze instructies).
    """
    main_data = load_json("main.json")
    mb_data = main_data.get("mbInstrument", {})
    print("\nStarten maar...\n")
    print("Selecteer uw rol:")
    print("1. Ik ben juridisch begeleider")
    print("2. Ik ben maatschappelijk begeleider")
    print("3. Ik ben begeleider voor nareizigers")
    rol_keuze = input("Voer het nummer van uw rol in: ").strip()
    if rol_keuze == "1":
        start_juridisch_begeleider()
    elif rol_keuze == "2":
        print("\nKies een optie voor het MB‑Instrument:")
        print("1. MB‑Instrument invullen")
        print("2. Bekijk begeleidende procedure")
        keuze = input("Maak uw keuze (1 of 2): ").strip()
        if keuze == "1":
            instrument = mb_data.get("mb_instrument", {})
            if not instrument:
                print("MB‑Instrument module niet gevonden in main.json.")
                return
            print(f"\n=== {instrument.get('title', 'MB‑Instrument')} ===")
            print(instrument.get("introductie", ""))
            print("\nOpmerking:")
            print(instrument.get("instructions", ""))
            all_questions = instrument.get("questions", [])
            answers = {}
            for question in all_questions:
                answer = ask_question(question)
                answers[question["nummer"]] = answer
            print("\n=== ALLE VRAGEN ZIJN BEANTWOORD ===")
            print("Hieronder een beknopt overzicht van uw antwoorden:")
            for q_num, ans in answers.items():
                print(f" - Vraag {q_num}: {ans}")
            print("\nEinde van het programma.")
        elif keuze == "2":
            procedure = mb_data.get("procedure", {})
            if not procedure:
                print("Procedure-module voor het MB‑Instrument niet gevonden in main.json.")
                return
            print(f"\n=== {procedure.get('procedureTitle', 'Maatschappelijke Begeleiding Procedure')} ===")
            print(procedure.get("inleiding", ""))
            print("\nFasen:")
            for fase in procedure.get("fasen", []):
                print(f"\nFase: {fase.get('fase', '')}")
                print(f"Beschrijving: {fase.get('beschrijving', '')}")
                if "voorlichting" in fase and fase["voorlichting"]:
                    print("Voorlichting:")
                    for punt in fase["voorlichting"].get("punten", []):
                        print(f" - {punt.get('id', '')}: {punt.get('tekst', '')}")
                if "acties" in fase and fase["acties"]:
                    print("Acties:")
                    for punt in fase["acties"].get("punten", []):
                        print(f" - {punt.get('id', '')}: {punt.get('tekst', '')}")
            print("\nDoelstellingen:")
            doelstellingen = procedure.get("doelstellingen", {})
            if isinstance(doelstellingen.get("hoofddoelen", []), list):
                for doel in doelstellingen.get("hoofddoelen", []):
                    print(f" - {doel}")
            else:
                print(doelstellingen.get("hoofddoelen", ""))
            print("\nBenodigde Vaardigheden:")
            for vaardigheid in procedure.get("benodigdeVaardigheden", []):
                print(f" - {vaardigheid}")
            print("\nVervolgplanning:")
            print(procedure.get("vervolgplanning", ""))
        else:
            print("Ongeldige keuze, standaard MB‑Instrument invullen wordt gestart.")
            instrument = mb_data.get("mb_instrument", {})
            print(f"\n=== {instrument.get('title', 'MB‑Instrument')} ===")
            print(instrument.get("introductie", ""))
            print("\nOpmerking:")
            print(instrument.get("instructions", ""))
            all_questions = instrument.get("questions", [])
            answers = {}
            for question in all_questions:
                answer = ask_question(question)
                answers[question["nummer"]] = answer
            print("\n=== ALLE VRAGEN ZIJN BEANTWOORD ===")
            print("Hieronder een beknopt overzicht van uw antwoorden:")
            for q_num, ans in answers.items():
                print(f" - Vraag {q_num}: {ans}")
            print("\nEinde van het programma.")
    elif rol_keuze == "3":
        start_nareizigers()
    else:
        print("Onbekende rol, standaard MB‑Instrument wordt gestart.")
        start_mb_instrument()

def start_juridisch_begeleider():
    main_data = load_json("main.json")
    print("\nWelkom! Omdat u hebt aangegeven dat u juridisch begeleider bent, kunt u kiezen uit de volgende modules:")
    print("1. Juridisch Onderwerp Kiezen")
    print("   (Krijg toegang tot actuele juridische informatie met externe zoekacties en fetch-resultaten.)")
    print("2. Starten van een specifieke juridische procedure")
    print("   (Bijvoorbeeld een MVV-aanvraag, gezinshereniging of inburgeringsprocedure begeleiden.)")
    print("3. Bespreken van een Juridische Casus")
    print("   (Stap-voor-stap begeleiding bij het analyseren van een individuele casus, inclusief advies en verslaglegging.)")
    keuze = input("\nTyp 1, 2 of 3 om uw keuze te maken: ").strip().lower()
    if keuze == "1":
        process_juridische_procedure(main_data)
    elif keuze == "2":
        choose_procedure()
    elif keuze == "3":
        start_casusanalyse(main_data)
    else:
        print("Ongeldige keuze. Probeer het opnieuw.")

def choose_procedure():
    procedures = load_json("procedures.json")
    print("\nU kunt de volgende procedures raadplegen:\n")
    for key, proc in procedures.items():
        print(f"{key}: {proc['title']}")
        print(f"   {proc['description']}\n")
    keuze = input("Geef het procodenummer of de titel in (bijv. PROC001 of MVV-aanvraag): ").strip()
    if keuze.upper() in procedures:
        selected_proc = procedures[keuze.upper()]
        print("\n=== PROCEDURE DETAILS ===")
        print(f"Titel: {selected_proc['title']}")
        print(f"Beschrijving: {selected_proc['description']}")
        print("Stappen:")
        for step in selected_proc["steps"]:
            print(f" - Stap {step['step']}: {step['description']}")
    else:
        found = False
        for key, proc in procedures.items():
            if keuze.lower() in proc["title"].lower():
                selected_proc = proc
                found = True
                print("\n=== PROCEDURE DETAILS ===")
                print(f"Titel: {selected_proc['title']}")
                print(f"Beschrijving: {selected_proc['description']}")
                print("Stappen:")
                for step in selected_proc["steps"]:
                    print(f" - Stap {step['step']}: {step['description']}")
                break
        if not found:
            print("Geen geldige keuze gemaakt.")

def start_casusanalyse(main_data):
    print("\nWilt u een juridische casus bespreken? (ja/nee)")
    antwoord = input().strip().lower()
    if antwoord != "ja":
        print("Oké, geen casusanalyse uitgevoerd.")
        return
    print("\nLaten we beginnen met de casusanalyse. Beantwoord alstublieft de volgende juridische vragen.")
    casus_data = {}
    casus_data["aanleiding"] = input("Wat is de juridische aanleiding van de casus? ")
    casus_data["rechtsbelang"] = input("Wat is het juridische belang voor de cliënt? ")
    casus_data["documenten"] = input("Beschrijf kort de relevante documenten of besluiten: ")
    casus_data["termijn"] = input("Is er een specifieke termijn of deadline? ")
    while True:
        extra = input("Zijn er nog andere relevante feiten of juridische aspecten? (typ 'nee' als alles duidelijk is) ")
        if extra.strip().lower() == "nee":
            break
        casus_data.setdefault("andere_feiten", []).append(extra)
    print("\n=== VERZAMELDE CASUSINFORMATIE ===")
    for key, value in casus_data.items():
        print(f"{key}: {value}")
    juridisch_advies = (
        "Op basis van de verstrekte informatie adviseren wij: Controleer het besluit grondig, verzamel alle relevante documenten en overweeg een formeel bezwaar. "
        "Neem contact op met een gespecialiseerde advocaat voor verdere begeleiding."
    )
    print("\n=== JURIDISCH ADVIES ===")
    print(juridisch_advies)
    verslag_keuze = input("\nWilt u deze casus en het juridisch advies in een verslag vastleggen? (ja/nee) ").strip().lower()
    if verslag_keuze == "ja":
        verslag = {
            "casus_data": casus_data,
            "juridisch_advies": juridisch_advies,
            "bronvermelding": "Gebruik de relevante officiële en erkende bronnen (zie juridischeProcedure in main.json)"
        }
        with open("JuridischVerslag.txt", "w", encoding="utf-8") as f:
            f.write("Juridisch Verslag\n")
            f.write("================\n")
            for key, value in verslag["casus_data"].items():
                f.write(f"{key}: {value}\n")
            f.write("\nJuridisch Advies:\n")
            f.write(juridisch_advies + "\n")
            f.write("\nBronvermelding:\n")
            f.write(verslag["bronvermelding"] + "\n")
        print("\nHet verslag is gegenereerd en opgeslagen als 'JuridischVerslag.txt'.")
    else:
        print("Casus en advies worden niet vastgelegd als verslag.")

def start_nareizigers():
    procedures = load_json("procedures.json")
    print("\nWelkom! U heeft gekozen voor de rol 'nareizigers'.")
    print("U kunt de volgende procedures raadplegen:\n")
    for key, proc in procedures.items():
        print(f"{key}: {proc['title']}")
        print(f"   {proc['description']}\n")
    keuze = input("Geef het procodenummer of de titel in (bijv. PROC001 of MVV-aanvraag): ").strip()
    if keuze.upper() in procedures:
        selected_proc = procedures[keuze.upper()]
        print("\n=== PROCEDURE DETAILS ===")
        print(f"Titel: {selected_proc['title']}")
        print(f"Beschrijving: {selected_proc['description']}")
        print("Stappen:")
        for step in selected_proc["steps"]:
            print(f" - Stap {step['step']}: {step['description']}")
    else:
        found = False
        for key, proc in procedures.items():
            if keuze.lower() in proc["title"].lower():
                selected_proc = proc
                found = True
                print("\n=== PROCEDURE DETAILS ===")
                print(f"Titel: {selected_proc['title']}")
                print(f"Beschrijving: {selected_proc['description']}")
                print("Stappen:")
                for step in selected_proc["steps"]:
                    print(f" - Stap {step['step']}: {step['description']}")
                break
        if not found:
            print("Geen geldige keuze gemaakt.")

def start_mb_instrument():
    """
    Start het traject voor Maatschappelijk Begeleider met betrekking tot het invullen van het MB‑Instrument.
    De gebruiker kan kiezen tussen:
      1. Het invullen van het MB‑Instrument (vragen uit de module 'mb_instrument').
      2. Het bekijken van de begeleidende procedure (stapsgewijze instructies).
    """
    main_data = load_json("main.json")
    mb_data = main_data.get("mbInstrument", {})
    print("\nStarten maar...\n")
    print("Selecteer uw rol:")
    print("1. Ik ben juridisch begeleider")
    print("2. Ik ben maatschappelijk begeleider")
    print("3. Ik ben begeleider voor nareizigers")
    rol_keuze = input("Voer het nummer van uw rol in: ").strip()
    if rol_keuze == "1":
        start_juridisch_begeleider()
    elif rol_keuze == "2":
        print("\nKies een optie voor het MB‑Instrument:")
        print("1. MB‑Instrument invullen")
        print("2. Bekijk begeleidende procedure")
        keuze = input("Maak uw keuze (1 of 2): ").strip()
        if keuze == "1":
            instrument = mb_data.get("mb_instrument", {})
            if not instrument:
                print("MB‑Instrument module niet gevonden in main.json.")
                return
            print(f"\n=== {instrument.get('title', 'MB‑Instrument')} ===")
            print(instrument.get("introductie", ""))
            print("\nOpmerking:")
            print(instrument.get("instructions", ""))
            all_questions = instrument.get("questions", [])
            answers = {}
            for question in all_questions:
                answer = ask_question(question)
                answers[question["nummer"]] = answer
            print("\n=== ALLE VRAGEN ZIJN BEANTWOORD ===")
            print("Hieronder een beknopt overzicht van uw antwoorden:")
            for q_num, ans in answers.items():
                print(f" - Vraag {q_num}: {ans}")
            print("\nEinde van het programma.")
        elif keuze == "2":
            procedure = mb_data.get("procedure", {})
            if not procedure:
                print("Procedure-module voor het MB‑Instrument niet gevonden in main.json.")
                return
            print(f"\n=== {procedure.get('procedureTitle', 'Maatschappelijke Begeleiding Procedure')} ===")
            print(procedure.get("inleiding", ""))
            print("\nFasen:")
            for fase in procedure.get("fasen", []):
                print(f"\nFase: {fase.get('fase', '')}")
                print(f"Beschrijving: {fase.get('beschrijving', '')}")
                if "voorlichting" in fase and fase["voorlichting"]:
                    print("Voorlichting:")
                    for punt in fase["voorlichting"].get("punten", []):
                        print(f" - {punt.get('id', '')}: {punt.get('tekst', '')}")
                if "acties" in fase and fase["acties"]:
                    print("Acties:")
                    for punt in fase["acties"].get("punten", []):
                        print(f" - {punt.get('id', '')}: {punt.get('tekst', '')}")
            print("\nDoelstellingen:")
            doelstellingen = procedure.get("doelstellingen", {})
            if isinstance(doelstellingen.get("hoofddoelen", []), list):
                for doel in doelstellingen.get("hoofddoelen", []):
                    print(f" - {doel}")
            else:
                print(doelstellingen.get("hoofddoelen", ""))
            print("\nBenodigde Vaardigheden:")
            for vaardigheid in procedure.get("benodigdeVaardigheden", []):
                print(f" - {vaardigheid}")
            print("\nVervolgplanning:")
            print(procedure.get("vervolgplanning", ""))
        else:
            print("Ongeldige keuze, standaard MB‑Instrument invullen wordt gestart.")
            instrument = mb_data.get("mb_instrument", {})
            print(f"\n=== {instrument.get('title', 'MB‑Instrument')} ===")
            print(instrument.get("introductie", ""))
            print("\nOpmerking:")
            print(instrument.get("instructions", ""))
            all_questions = instrument.get("questions", [])
            answers = {}
            for question in all_questions:
                answer = ask_question(question)
                answers[question["nummer"]] = answer
            print("\n=== ALLE VRAGEN ZIJN BEANTWOORD ===")
            print("Hieronder een beknopt overzicht van uw antwoorden:")
            for q_num, ans in answers.items():
                print(f" - Vraag {q_num}: {ans}")
            print("\nEinde van het programma.")
    elif rol_keuze == "3":
        start_nareizigers()
    else:
        print("Onbekende rol, standaard MB‑Instrument wordt gestart.")
        start_mb_instrument()

def start_juridisch_begeleider():
    main_data = load_json("main.json")
    print("Welkom juridisch begeleider!")
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def start():
    return {"status": "GPT-plugin backend is actief"}
