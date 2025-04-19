#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
from typing import List, Dict, Any

# Betrouwbare domeinen
BETROUWBARE_DOMAINS: List[str] = [
   "rijksoverheid.nl", "ind.nl", "ministerievanbuitenlandsezaken.nl", "ministerievanjustitie.nl", 
    "ministerievanfinancien.nl", "ministerievanonderwijs.nl", "regering.nl", "nederlandwereldwijd.nl", 
    "europa.eu", "ec.europa.eu", "europarl.europa.eu", "eurojust.europa.eu", "eur-lex.europa.eu", 
    "hudoc.echr.coe.int", "un.org", "unhcr.org", "unicef.org", "icrc.org", "redcross.org", 
    "amnesty.nl", "amnesty.org", "vluchtelingenwerk.nl", "juridischloket.nl", "migratierecht.nl", 
    "integratiefonds.nl", "inburgeren.nl", "kiesraad.nl", "nrc.nl", "volkskrant.nl", 
    "parlement.com", "oecd.org", "narcis.nl", "wodc.nl", "unicef.nl", "inspectiegezondheidszorg.nl", 
    "zorginstituutnederland.nl", "pharos.nl", "ministerievangezondheid.nl", "europalegal.eu", 
    "ecrea.org", "officialeuropeannews.eu", "rechtsinformatie.nl", "brp.nl", "omroepbrabant.nl", 
    "europeanpolicycentre.eu", "europaneconomic.org", "ministerievanarbeid.nl", "arbeidsinspectie.nl", 
    "politieke-partijen.nl", "cpb.nl", "scp.nl", "inspectieonderwijs.nl", "regeerders.nl", 
    "ministerievancultureel-erfgoed.nl", "overheidspublicaties.nl", "ambtenarenbond.nl", "bijdl.nl", 
    "volksgezondheid.nl", "sociaalzaken.nl", "integratieadvies.nl", "migrantinstitute.nl", 
    "immigratieadvies.nl", "internationalmigration.org", "fhi.no", "ukri.org", "europamigration.eu", 
    "migratieforum.nl", "verhuisadvies.nl", "logistiek.nl", "socialezekerheid.eu", "multicultureelcentrum.nl", 
    "cultureelplatform.nl", "jongerenwerk.nl", "arbeidsmarktinformatie.nl", "krantenvanhetnoorden.nl", 
    "parlementairdocument.nl", "europapress.eu", "documentenbank.nl", "advocatenorde.nl", 
    "rechtspraakvooriedereen.nl", "sociaalekennisbank.nl", "overheidstransparant.nl", "ministerievanmilieu.nl", 
    "gemeentelijkezorg.nl", "gezondheidsmonitor.nl", "europainnovatie.eu", "dutchinnovation.nl", 
    "integratieplatform.nl", "migratieanalyse.nl", "sociaalbeleid.nl", "europabureau.nl", 
    "internationaalrecht.nl", "legalinfo.nl", "rechtdata.nl", "verblijfsvergunninginfo.nl", 
    "migrantadvies.org", "integratiewetgeving.nl", "europeanpolicycentre.eu"
]

# Relevante sleutelwoorden
SLEUTELWOORDEN: List[str] = [
    "asiel", "statushouder", "vluchteling", "vreemdeling", "opvang",
    "procedure", "verblijf", "migratie", "migrant", "inburgering"
]

# Nederlandse context-termen
DOELGROEP_NL: List[str] = [
    "nederland", "nederlandse", "gemeente", "wetgeving", "beleid", "migratie"
]

def check_url(url: str, timeout: int = 5) -> bool:
    """Controleert of een URL bereikbaar is."""
    try:
        resp = requests.head(url, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False

def is_relevante_bron(url: str) -> bool:
    url = url.lower()
    return any(domein in url for domein in BETROUWBARE_DOMAINS)

def bevat_relevante_term(tekst: str) -> bool:
    tekst = tekst.lower()
    return any(kw in tekst for kw in SLEUTELWOORDEN)

def is_gericht_op_nederland(tekst: str) -> bool:
    tekst = tekst.lower()
    return any(nl in tekst for nl in DOELGROEP_NL)

def filter_resultaten(resultaten: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtert de zoekresultaten op betrouwbare bron, relevante trefwoorden en NL-context.
    """
    gefilterd = []
    for r in resultaten:
        url = r.get("link", "")
        titel = r.get("titel", "")
        samenvatting = r.get("samenvatting", "")
        if not is_relevante_bron(url):
            continue
        if not (bevat_relevante_term(titel) or bevat_relevante_term(samenvatting)):
            continue
        if not (is_gericht_op_nederland(titel) or is_gericht_op_nederland(samenvatting)):
            continue
        gefilterd.append(r)
    return gefilterd

def format_apa(titel: str, url: str, datum: str) -> str:
    """
    Eenvoudige APA‑stijl formattering.
    Bijvoorbeeld: Titel. (2025, April 19). Geraadpleegd van URL
    """
    return f"{titel}. ({datum}). Geraadpleegd van {url}"
