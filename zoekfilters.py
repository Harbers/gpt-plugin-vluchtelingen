#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import requests
from typing import List, Dict, Any, Tuple

BETROUWBARE_DOMAINS = [ ... ]  # zoals eerder
SLEUTELWOORDEN = [ ... ]
DOELGROEP_NL = [ ... ]

def check_url(url: str, timeout: int = 5) -> bool:
    try:
        resp = requests.head(url, timeout=timeout)
        return resp.status_code == 200
    except:
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
    gefilterd = []
    for r in resultaten:
        url = r.get("link","")
        titel = r.get("titel","")
        samenv = r.get("samenvatting","")
        if is_relevante_bron(url) and (bevat_relevante_term(titel) or bevat_relevante_term(samenv)) and (is_gericht_op_nederland(titel) or is_gericht_op_nederland(samenv)):
            gefilterd.append(r)
    return gefilterd

def format_apa(titel: str, url: str, datum: str) -> str:
    # eenvoudige APA: Titel. (YYYY, MMMM DD). Geraadpleegd van URL
    return f"{titel}. ({datum}). Geraadpleegd van {url}"
