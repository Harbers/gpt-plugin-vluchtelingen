import re
from typing import List, Dict

# Lijst met toegestane domeinen (Nederlandse en Europese overheid en semi-overheid, en erkende organisaties)
TOEGESTANE_DOMAINS = [
    r"\.overheid\.nl",
    r"\.rijksoverheid\.nl",
    r"\.minszw\.nl",
    r"\.minjenv\.nl",
    r"\.nederlandwereldwijd\.nl",
    r"\.europa\.eu",
    r"\.ec\.europa\.eu",
    r"\.rechtspraak\.nl",
    r"\.ind\.nl",
    r"\.coa\.nl",
    r"\.raadvanstate\.nl",
    r"\.vluchtelingenwerk\.nl",
    r"\.nidos\.nl",
    r"\.forensischinstituut\.nl",
    r"\.advocatenorde\.nl",
    r"\.raadvoorrechtsbijstand\.nl",
    r"\.rekenkamer\.nl"
]

# Sleutelwoorden die gerelateerd zijn aan asiel, vreemdelingen, statushouders, etc.
SLEUTELWOORDEN = [
    "asiel", "statushouder", "vluchteling", "vreemdeling", "opvang",
    "procedure", "verblijf", "migratie", "migrant", "indiening", "inburgering"
]

# Termen die aangeven dat de informatie gericht is op de Nederlandse doelgroep
DOELGROEP_NL = [
    "nederland", "nederlandse", "rijksoverheid", "gemeente", "wetgeving"
]

def is_relevante_bron(url: str) -> bool:
    """
    Controleer of de URL afkomstig is van een erkende (semi-)overheidsbron.
    """
    for pattern in TOEGESTANE_DOMAINS:
        if re.search(pattern, url):
            return True
    return False

def bevat_relevante_term(tekst: str) -> bool:
    """
    Controleer of de gegeven tekst één of meerdere van de relevante sleutelwoorden bevat.
    """
    tekst = tekst.lower()
    return any(kw in tekst for kw in SLEUTELWOORDEN)

def is_gericht_op_nederland(tekst: str) -> bool:
    """
    Controleer of de gegeven tekst termen bevat die wijzen op een Nederlandse context.
    """
    tekst = tekst.lower()
    return any(nl in tekst for nl in DOELGROEP_NL)

def filter_resultaten(resultaten: List[Dict]) -> List[Dict]:
    """
    Filtert de zoekresultaten op basis van:
      1. De URL moet afkomstig zijn van een toegestane bron.
      2. De titel of samenvatting moet relevante trefwoorden bevatten.
      3. De inhoud moet gericht zijn op de Nederlandse doelgroep.
    Alleen resultaten die aan alle voorwaarden voldoen worden behouden.
    """
    gefilterd = []
    for resultaat in resultaten:
        url = resultaat.get("link", "").lower()
        titel = resultaat.get("titel", "").lower()
        samenvatting = resultaat.get("samenvatting", "").lower()
        # Filteren op basis van de bron
        if not is_relevante_bron(url):
            continue
        # Filteren op relevante zoektermen in titel of samenvatting
        if not (bevat_relevante_term(titel) or bevat_relevante_term(samenvatting)):
            continue
        # Filteren op Nederlandse context
        if not (is_gericht_op_nederland(titel) or is_gericht_op_nederland(samenvatting)):
            continue

        gefilterd.append(resultaat)
    return gefilterd
