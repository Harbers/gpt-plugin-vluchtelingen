#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module: zoekfilters.py
Deze module implementeert uitgebreide zoekresultaat filtering voor de juridische zoekfunctie.
Het combineert de controle op betrouwbare bronnen, relevante sleutelwoorden en een Nederlandse context,
en anonimiseert privacygevoelige gegevens.
"""

import re
from typing import List, Dict, Any, Tuple

# ============================================================
# Configuratie en Constanten
# ============================================================

BETROUWBARE_DOMAINS = [
    r"\.overheid\.nl",
    r"\.rijksoverheid\.nl",
    r"\.minszw\.nl",
    r"\.minjenv\.nl",
    r"\.nederlandwereldwijd\.nl",
    r"\.europa\.eu",
    r"\.ec\.europa\.eu",
    r"\.europarl\.europa\.eu",
    r"\.eur-lex\.europa\.eu",
    r"\.hudoc\.echr\.coe\.int",
    r"\.un\.org",
    r"\.unhcr\.org",
    r"\.unicef\.org",
    r"\.icrc\.org",
    r"\.redcross\.org",
    r"\.amnesty\.nl",
    r"\.amnesty\.org",
    r"\.vluchtelingenwerk\.nl",
    r"\.juridischloket\.nl",
    r"\.migratierecht\.nl",
    r"\.integratiefonds\.nl",
    r"\.inburgeren\.nl",
    r"\.kiesraad\.nl",
    r"\.nrc\.nl",
    r"\.volkskrant\.nl",
    r"\.parlement\.com",
    r"\.oecd\.org",
    r"\.narcis\.nl",
    r"\.wodc\.nl",
    r"\.unicef\.nl",
    r"\.inspectiegezondheidszorg\.nl",
    r"\.zorginstituutnederland\.nl",
    r"\.pharos\.nl",
    r"\.ministerievangezondheid\.nl",
    r"\.europalegal\.eu",
    r"\.ecrea\.org",
    r"\.officialeuropeannews\.eu",
    r"\.rechtsinformatie\.nl",
    r"\.brp\.nl",
    r"\.omroepbrabant\.nl",
    r"\.europeanpolicycentre\.eu",
    r"\.europaneconomic\.org",
    r"\.ministerievanarbeid\.nl",
    r"\.arbeidsinspectie\.nl",
    r"\.politieke-partijen\.nl",
    r"\.cpb\.nl",
    r"\.scp\.nl",
    r"\.inspectieonderwijs\.nl",
    r"\.regeerders\.nl",
    r"\.ministerievancultureel-erfgoed\.nl",
    r"\.overheidspublicaties\.nl",
    r"\.ambtenarenbond\.nl",
    r"\.bijdl\.nl",
    r"\.volksgezondheid\.nl",
    r"\.sociaalzaken\.nl",
    r"\.integratieadvies\.nl",
    r"\.migrantinstitute\.nl",
    r"\.immigratieadvies\.nl",
    r"\.internationalmigration\.org",
    r"\.fhi\.no",
    r"\.ukri\.org",
    r"\.europamigration\.eu",
    r"\.migratieforum\.nl",
    r"\.verhuisadvies\.nl",
    r"\.logistiek\.nl",
    r"\.socialezekerheid\.eu",
    r"\.multicultureelcentrum\.nl",
    r"\.cultureelplatform\.nl",
    r"\.jongerenwerk\.nl",
    r"\.arbeidsmarktinformatie\.nl",
    r"\.krantenvanhetnoorden\.nl",
    r"\.parlementairdocument\.nl",
    r"\.europapress\.eu",
    r"\.documentenbank\.nl",
    r"\.advocatenorde\.nl",
    r"\.rechtspraakvooriedereen\.nl",
    r"\.sociaalekennisbank\.nl",
    r"\.overheidstransparant\.nl",
    r"\.ministerievanmilieu\.nl",
    r"\.gemeentelijkezorg\.nl",
    r"\.gezondheidsmonitor\.nl",
    r"\.europainnovatie\.eu",
    r"\.dutchinnovation\.nl",
    r"\.integratieplatform\.nl",
    r"\.migratieanalyse\.nl",
    r"\.sociaalbeleid\.nl",
    r"\.europabureau\.nl",
    r"\.internationaalrecht\.nl",
    r"\.legalinfo\.nl",
    r"\.rechtdata\.nl",
    r"\.verblijfsvergunninginfo\.nl",
    r"\.migrantadvies\.org",
    r"\.integratiewetgeving\.nl"
]

SLEUTELWOORDEN = [
    "asiel", "statushouder", "vluchteling", "vreemdeling", "opvang",
    "procedure", "verblijf", "migratie", "migrant", "indiening", "inburgering"
]

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
    for pattern in BETROUWBARE_DOMAINS:
        if re.search(pattern, url):
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
    Alleen resultaten die aan alle voorwaarden voldoen worden behouden.
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

def controleer_gevoelige_data(invoer: str) -> Tuple[str, List[str]]:
    """
    Vervang privacygevoelige informatie (zoals BSN, V-nummers, namen) door een placeholder.
    """
    meldingen = []
    # V‑nummer controle: detecteer 'V' gevolgd door 6 tot 9 cijfers (case-insensitive)
    patroon_vnummer = re.compile(r'\bV\d{6,9}\b', re.IGNORECASE)
    if patroon_vnummer.search(invoer):
        meldingen.append("Gebruik van een V‑nummer is niet toegestaan.")
        invoer = patroon_vnummer.sub("[ANONIEM]", invoer)
    # BSN controle: zoek naar 8 of 9 cijferige getallen
    patroon_bsn = re.compile(r'\b\d{8,9}\b')
    for match in patroon_bsn.findall(invoer):
        if len(match) == 9 and is_valid_bsn(match):
            meldingen.append("Gebruik van een BSN-nummer is niet toegestaan.")
            invoer = invoer.replace(match, "[ANONIEM]")
        elif len(match) == 8:
            meldingen.append("Gebruik van een BSN-nummer is niet toegestaan.")
            invoer = invoer.replace(match, "[ANONIEM]")
    # Naamcontrole: detecteer twee opeenvolgende woorden met hoofdletters
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
