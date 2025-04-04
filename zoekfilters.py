#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import List, Dict, Any

# ============================================================
# Configuratie en Constanten
# ============================================================

# Uitgebreide lijst met betrouwbare domeinen (maximaal 100 punten) voor het filteren van zoekresultaten.
BETROUWBARE_DOMAINS = [
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

# Sleutelwoorden die relevant zijn voor asiel, vluchtelingen, etc.
SLEUTELWOORDEN = [
    "asiel", "statushouder", "vluchteling", "vreemdeling", "opvang",
    "procedure", "verblijf", "migratie", "migrant", "indiening", "inburgering"
]

# Termen die wijzen op een Nederlandse context
DOELGROEP_NL = [
    "nederland", "nederlandse", "rijksoverheid", "gemeente", "wetgeving"
]

# ============================================================
# Functies voor Controle en Filtering van Zoekresultaten
# ============================================================

def is_relevante_bron(url: str) -> bool:
    """
    Controleer of de URL afkomstig is van een van de betrouwbare domeinen.
    """
    url = url.lower()
    for domein in BETROUWBARE_DOMAINS:
        if domein in url:
            return True
    return False

def bevat_relevante_term(tekst: str) -> bool:
    """
    Controleer of de gegeven tekst één of meer van de relevante sleutelwoorden bevat.
    """
    tekst = tekst.lower()
    return any(kw in tekst for kw in SLEUTELWOORDEN)

def is_gericht_op_nederland(tekst: str) -> bool:
    """
    Controleer of de tekst termen bevat die wijzen op een Nederlandse context.
    """
    tekst = tekst.lower()
    return any(nl in tekst for nl in DOELGROEP_NL)

def filter_resultaten(resultaten: List[Dict]) -> List[Dict]:
    """
    Filtert de zoekresultaten op basis van:
      1. De URL moet afkomstig zijn van een betrouwbare bron.
      2. De titel of samenvatting moet relevante trefwoorden bevatten.
      3. De inhoud moet gericht zijn op de Nederlandse context.
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
    Controleer of een 9-cijferig BSN voldoet aan de 11-proef.
    """
    if len(bsn) != 9 or not bsn.isdigit():
        return False
    try:
        total = sum(int(bsn[i]) * (9 - i) for i in range(8)) - int(bsn[8])
        return total % 11 == 0
    except Exception:
        return False

def controleer_gevoelige_data(invoer: str) -> (str, List[str]):
    """
    Vervang privacygevoelige informatie (zoals BSN, V-nummers, namen) door een placeholder.
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
    Verwerkt de invoer door privacygevoelige gegevens te anonimiseren.
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
    Combineert filters op basis van de data.
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
