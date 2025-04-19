#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
from typing import List, Dict, Any, Tuple

# ============================================================
# Configuratie en Constanten
# ============================================================

# Uitgebreide lijst met betrouwbare domeinen voor het filteren van zoekresultaten.
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

# Relevante sleutelwoorden voor asiel, vluchtelingen, etc.
SLEUTELWOORDEN: List[str] = [
    "asiel", "statushouder", "vluchteling", "vreemdeling", "opvang",
    "procedure", "verblijf", "migratie", "migrant", "indiening", "inburgering"
]

# Termen die wijzen op een Nederlandse context
DOELGROEP_NL: List[str] = [
    "nederland", "nederlandse", "rijksoverheid", "gemeente", "wetgeving"
]

# ============================================================
# URL Validatie Functies
# ============================================================

def check_url(url: str, timeout: int = 5) -> bool:
    """
    Voert een HEAD-request uit om te controleren of de URL bereikbaar is en status code 200 retourneert.
    
    :param url: De URL die gecontroleerd dient te worden.
    :param timeout: Tijdslimiet voor de request.
    :return: True als de URL bereikbaar is, anders False.
    """
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False

def get_valid_url(url: str, fallback_url: str = None) -> str:
    """
    Controleert of de opgegeven URL geldig is. Indien niet, retourneert deze de fallback_url (als deze geldig is).
    
    :param url: De primaire URL.
    :param fallback_url: Een alternatieve URL als fallback.
    :return: De geldige URL of een lege string indien geen van beide geldig is.
    """
    if check_url(url):
        return url
    elif fallback_url and check_url(fallback_url):
        return fallback_url
    else:
        return ""

# ============================================================
# Functies voor Controle en Filtering van Zoekresultaten
# ============================================================

def is_relevante_bron(url: str) -> bool:
    """
    Controleert of de URL afkomstig is van een betrouwbare bron.
    
    :param url: De URL die gecontroleerd dient te worden.
    :return: True als de URL afkomstig is van een betrouwbare bron, anders False.
    """
    url = url.lower()
    return any(domein in url for domein in BETROUWBARE_DOMAINS)

def bevat_relevante_term(tekst: str) -> bool:
    """
    Controleert of de tekst één of meer relevante sleutelwoorden bevat.
    
    :param tekst: De te controleren tekst.
    :return: True als een of meer sleutelwoorden aanwezig zijn, anders False.
    """
    tekst = tekst.lower()
    return any(kw in tekst for kw in SLEUTELWOORDEN)

def is_gericht_op_nederland(tekst: str) -> bool:
    """
    Controleert of de tekst termen bevat die wijzen op een Nederlandse context.
    
    :param tekst: De te controleren tekst.
    :return: True als Nederlandse termen aanwezig zijn, anders False.
    """
    tekst = tekst.lower()
    return any(nl in tekst for nl in DOELGROEP_NL)

def filter_resultaten(resultaten: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtert de zoekresultaten op basis van betrouwbare bron, relevante trefwoorden en Nederlandse context.
    
    :param resultaten: Lijst met zoekresultaten.
    :return: Gefilterde lijst met relevante resultaten.
    """
    gefilterd = []
    for resultaat in resultaten:
        url = resultaat.get("link", "").lower()
        titel = resultaat.get("titel", "").lower()
        samenvatting = resultaat.get("samenvatting", "").lower()
        if not is_relevante_bron(url):
            continue
        if not (bevat_relevante_term(titel) or bevat_relevante_term(samenvatting)):
            continue
        if not (is_gericht_op_nederland(titel) or is_gericht_op_nederland(samenvatting)):
            continue
        gefilterd.append(resultaat)
    return gefilterd

# ============================================================
# Functies voor Anonimisering van Gevoelige Gegevens
# ============================================================

def is_valid_bsn(bsn: str) -> bool:
    """
    Controleert of een BSN geldig is.
    
    :param bsn: De BSN als string.
    :return: True als het BSN geldig is, anders False.
    """
    if len(bsn) != 9 or not bsn.isdigit():
        return False
    try:
        total = sum(int(bsn[i]) * (9 - i) for i in range(8)) - int(bsn[8])
        return total % 11 == 0
    except Exception:
        return False

def controleer_gevoelige_data(invoer: str) -> Tuple[str, List[str]]:
    """
    Vervangt gevoelige gegevens (zoals V-nummers, BSN's en namen) door een placeholder en geeft meldingen terug.
    
    :param invoer: De oorspronkelijke tekst.
    :return: Een tuple met de geanonimiseerde tekst en een lijst met meldingen.
    """
    meldingen = []
    patroon_vnummer = re.compile(r'\bV\d{6,9}\b', re.IGNORECASE)
    if patroon_vnummer.search(invoer):
        meldingen.append("Gebruik van een V‑nummer is niet toegestaan.")
        invoer = patroon_vnummer.sub("[ANONIEM]", invoer)
    patroon_bsn = re.compile(r'\b\d{8,9}\b')
    for match in patroon_bsn.findall(invoer):
        if len(match) == 9 and is_valid_bsn(match):
            meldingen.append("Gebruik van een BSN-nummer is niet toegestaan.")
            invoer = invoer.replace(match, "[ANONIEM]")
        elif len(match) == 8:
            meldingen.append("Gebruik van een BSN-nummer is niet toegestaan.")
            invoer = invoer.replace(match, "[ANONIEM]")
    patroon_naam = re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b')
    if patroon_naam.search(invoer):
        meldingen.append("Gebruik van een naam is niet toegestaan.")
        invoer = patroon_naam.sub("[ANONIEM]", invoer)
    return invoer, meldingen

def verwerk_invoer(invoer: str) -> Dict[str, Any]:
    """
    Verwerkt de invoer door gevoelige data te anonimiseren en retourneert de geanonimiseerde tekst samen met eventuele meldingen.
    
    :param invoer: De oorspronkelijke invoer.
    :return: Een dictionary met de geanonimiseerde invoer, meldingen en een statusboodschap.
    """
    anonieme_invoer, meldingen = controleer_gevoelige_data(invoer)
    return {
        "geanonimiseerde_invoer": anonieme_invoer,
        "meldingen": meldingen,
        "status": "verwerking voortgezet zonder gevoelige gegevens"
    }

# ============================================================
# Overige Helper-functies
# ============================================================
def combineer_filters(data: str) -> str:
    """
    Converteert de input naar lowercase voor consistente filtering.
    
    :param data: De te verwerken data.
    :return: De data in lowercase.
    """
    return data.lower()

# ============================================================
# Main Block voor Testen
# ============================================================
if __name__ == "__main__":
    test_invoer = "De cliënt Jan Jansen heeft een V1234567 en BSN 123456782."
    print("Originele invoer:", test_invoer)
    resultaat = verwerk_invoer(test_invoer)
    print("Geanonimiseerde invoer:", resultaat["geanonimiseerde_invoer"])
    print("Meldingen:", resultaat["meldingen"])
