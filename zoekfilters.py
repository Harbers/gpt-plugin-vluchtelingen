#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import List, Dict, Tuple, Any

# ============================================================
# Configuratie en Constanten
# ============================================================

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

# Datastructuur met zoektermen onderverdeeld in 20 onderwerpen.
ZOEKTERMEN: Dict[str, Dict[str, Dict[str, List[str] or str]]] = {
    "Onderwerp1": {
        "Procedureel Asiel": {
            "subthemas": [
                "Aanvraag VOTA",
                "Asielprocedure",
                "Aanmeldfase",
                "(ge)horen",
                "sporenbeleid",
                "beslistermijn",
                "moratoria",
                "dwangsommen",
                "overschrijding beslistermijnen"
            ],
            "uitleg": "Aanvraag verblijfsvergunning onbepaalde tijd asiel met aandacht voor procedures, termijnen en dwangsommen."
        },
        "Bewijs en documenten": {
            "subthemas": [
                "Medische onderzoeken",
                "iMMO",
                "Medifirst",
                "FMMU",
                "NFI/NIFP",
                "medisch steunbewijs",
                "leeftijdsschouwing",
                "taalanalyse",
                "geloofwaardigheidsbeoordeling",
                "Bureau Documenten"
            ],
            "uitleg": "Verzamelen van alle benodigde bewijzen en documenten ter ondersteuning van de asielaanvraag."
        }
    },
    "Onderwerp2": {
        "Grensprocedure": {
            "subthemas": ["grensdetentie", "vreemdelingenbewaring"],
            "uitleg": "Beheer en uitvoering van procedures bij grenscontrole en detentie."
        },
        "Internationaal procederen": {
            "subthemas": [
                "EHRM",
                "HvJEU",
                "VN Kinderrechtencomité",
                "Comité tegen Foltering (CAT)",
                "Interim measure",
                "Klachten (asiel)",
                "Nationale ombudsman",
                "klachten over rechtshulpverleners",
                "Herhaalde aanvragen",
                "nova",
                "ontvankelijkheid"
            ],
            "uitleg": "Juridische procedures op internationaal niveau voor asielzaken, inclusief klachtenprocedures."
        }
    },
    "Onderwerp3": {
        "Rechtsmiddelen asiel": {
            "subthemas": ["beroep", "hoger beroep", "voorlopige voorziening", "schorsende werking"],
            "uitleg": "Gebruik van juridische rechtsmiddelen ter bestrijding van afwijzingen en intrekkingen."
        },
        "Toelatingsgronden": {
            "subthemas": [
                "3 EVRM",
                "subsidiaire bescherming",
                "non-refoulement",
                "indirect refoulement",
                "15c uitzonderlijke situatie",
                "willekeurig geweld",
                "glijdende schaal",
                "dienstweigering",
                "desertie",
                "gewetensbezwaren",
                "inzet tegen eigen volk",
                "etniciteit vervolging",
                "etnische groepen"
            ],
            "uitleg": "Criteria en gronden voor toelating tot asiel en bescherming op basis van internationale standaarden."
        }
    },
    "Onderwerp4": {
        "Kinderen": {
            "subthemas": [
                "zelfstandige asielmotieven",
                "meereizende kinderen",
                "kindspecifieke daden van vervolging",
                "lagere drempel"
            ],
            "uitleg": "Specifieke aandacht voor de asielprocedures van minderjarige en meereizende kinderen."
        },
        "LHBTI": {
            "subthemas": [
                "LHBTIQ+",
                "ondergrens",
                "lesbiennes",
                "homoseksuelen",
                "biseksuelen",
                "transpersonen",
                "intersekse",
                "queer"
            ],
            "uitleg": "Beoordeling en bescherming van LHBTI-asielzoekers."
        }
    },
    "Onderwerp5": {
        "Palestijnen / art. 1D": {
            "subthemas": [
                "UNRWA",
                "uitsluitings- en insluitingsgrond art. 1D",
                "gebruikelijke woon- en verblijfplaats"
            ],
            "uitleg": "Juridische criteria voor Palestijnse asielzoekers conform art. 1D van het Vluchtelingenverdrag."
        },
        "Nationaliteit, identiteit en herkomst": {
            "subthemas": [
                "ongeloofwaardige nationaliteit",
                "misleiding",
                "nationaliteitsverklaring",
                "valse documenten",
                "herkomstonderzoek"
            ],
            "uitleg": "Onderzoek en beoordeling van de authenticiteit van identiteit en herkomst van asielzoekers."
        }
    },
    "Onderwerp6": {
        "Religie": {
            "subthemas": [
                "vervolging op grond van geloofsovertuiging",
                "bekering",
                "afvalligheid",
                "atheïsme",
                "geloofsgroei"
            ],
            "uitleg": "Informatie over vervolging op basis van religieuze overtuigingen."
        },
        "Vluchtelingschap": {
            "subthemas": [
                "vluchtelingenverdrag",
                "vervolgingsgronden",
                "réfugie sur place",
                "discriminatie"
            ],
            "uitleg": "Aspecten van vluchtelingschap en de toepassing van het vluchtelingenverdrag."
        }
    },
    "Onderwerp7": {
        "Afwijzings- en intrekkingsgronden asiel": {
            "subthemas": [
                "uitsluiting Vluchtelingenverdrag",
                "oorlogsmisdaden",
                "persoonlijke betrokkenheid",
                "persoonlijk vrijwaren",
                "bescherming door autoriteiten",
                "beschermingsalternatief",
                "vestigingsalternatief",
                "vluchtalternatief"
            ],
            "uitleg": "Gronden voor afwijzing en intrekking van asielvergunningen."
        },
        "Dublinverordening": {
            "subthemas": [
                "Dublinclaimanten",
                "interstatelijk vertrouwensbeginsel",
                "overdracht",
                "overname (Dublin)",
                "terugname (Dublin)",
                "leeftijdsschouwing en onderzoek"
            ],
            "uitleg": "Procedures en criteria in het kader van de Dublinverordening."
        }
    },
    "Onderwerp8": {
        "Geloofwaardigheid": {
            "subthemas": [
                "tegenstrijdige verklaringen",
                "documenten",
                "IND-werkinstructie"
            ],
            "uitleg": "Beoordeling van de geloofwaardigheid van de verstrekte informatie."
        },
        "Intrekking asielvergunning": {
            "subthemas": [
                "intrekking vbta of vota",
                "onjuiste gegevens",
                "openbare orde",
                "vervallen verleningsgrond",
                "herbeoordeling",
                "intrekkingsprocedure"
            ],
            "uitleg": "Procedures voor het intrekken van asielvergunningen op basis van onjuiste of misleidende informatie."
        }
    },
    "Onderwerp9": {
        "Openbare orde": {
            "subthemas": [
                "plegen misdrijven",
                "nationale veiligheid",
                "ongewenstverklaring"
            ],
            "uitleg": "Maatregelen en criteria gericht op het handhaven van de openbare orde."
        },
        "Veilig derde land": {
            "subthemas": [
                "niet-ontvankelijkheid",
                "eerder verblijf in derde land",
                "vestigingsalternatief in derde land",
                "art. 38"
            ],
            "uitleg": "Criteria voor niet-ontvankelijkheid op basis van verblijf in een veilig derde land."
        }
    },
    "Onderwerp10": {
        "Procedurerichtlijn": {
            "subthemas": [
                "kennelijk ongegrond",
                "procedure in spoor 2",
                "art. 36",
                "uitzonderingsgronden"
            ],
            "uitleg": "Richtlijnen voor procedures wanneer asielaanvragen kennelijk ongegrond zijn."
        },
        "EU-statushouders": {
            "subthemas": [
                "niet-ontvankelijkheid",
                "internationale bescherming in andere EU-lidstaat",
                "interstatelijk vertrouwensbeginsel",
                "bijzondere kwetsbaarheid"
            ],
            "uitleg": "Behandeling van asielaanvragen van EU-statushouders binnen een internationale context."
        }
    },
    "Onderwerp11": {
        "Gezinshereniging asiel": {
            "subthemas": [
                "voorwaarden gezinshereniging",
                "procedure gezinshereniging",
                "veelgestelde vragen reisroutes",
                "veelgestelde vragen gezinshereniging"
            ],
            "uitleg": "Juridische en praktische aspecten van gezinshereniging voor asielzoekers."
        },
        "Gezinshereniging regulier": {
            "subthemas": [
                "procedure toegang en verblijf",
                "voorwaarden verblijf bij echtgenoot/partner",
                "voorwaarden verblijf bij ouder"
            ],
            "uitleg": "Procedures voor reguliere gezinshereniging conform internationale regelgeving, inclusief art. 8 EVRM."
        }
    },
    "Onderwerp12": {
        "Reguliere verblijfsvergunning": {
            "subthemas": ["aanvraag reguliere verblijfsvergunning"],
            "uitleg": "Procedures voor de aanvraag en verlenging van reguliere verblijfsvergunningen."
        },
        "AMV / Gewortelde kinderen": {
            "subthemas": [
                "alleenstaande minderjarige vreemdeling",
                "adequate opvang",
                "buitenschuldvergunning",
                "terugkeerbesluit",
                "overgangsregeling",
                "Kinderpardon",
                "definitieve kinderregeling"
            ],
            "uitleg": "Specifieke procedures en voorwaarden voor minderjarige asielzoekers en integratie van kinderen."
        }
    },
    "Onderwerp13": {
        "Buitenschuld": {
            "subthemas": ["buitenschuldvergunning", "DT&V"],
            "uitleg": "Regelingen omtrent buitenschuld en de daarbij behorende vergunningen."
        },
        "Humanitair niet tijdelijk": {
            "subthemas": [
                "vbtr-humanitair niet tijdelijk",
                "voorwaarden na gezinshereniging/8 EVRM",
                "voorwaarden na medisch",
                "voorwaarden na tijdelijk humanitair",
                "8 EVRM/privéleven",
                "Afsluitingsregeling"
            ],
            "uitleg": "Voorwaarden en procedures voor humanitair niet-tijdelijk verblijf."
        }
    },
    "Onderwerp14": {
        "Medisch": {
            "subthemas": [
                "artikel 64",
                "uitstel van vertrek",
                "Vbt-r medisch",
                "feitelijke toegankelijkheid",
                "medische noodsituatie",
                "identiteit en nationaliteit",
                "BMA",
                "3 EVRM"
            ],
            "uitleg": "Medische aspecten binnen asielprocedures, inclusief noodsituaties en uitstel van vertrek."
        },
        "Mensenhandel": {
            "subthemas": [
                "mensenhandel",
                "schrijnendheid voorwaarden voor verblijfsvergunning op grond van schrijnendheid"
            ],
            "uitleg": "Behandeling van zaken omtrent mensenhandel en de voorwaarden voor verblijfsvergunning op basis van schrijnendheid."
        }
    },
    "Onderwerp15": {
        "Reguliere vergunning": {
            "subthemas": ["vergunning aanvraag", "aanvraag reguliere verblijfsvergunning"],
            "uitleg": "Procedurele aspecten van het aanvragen van reguliere vergunningen."
        },
        "Bezwaar en (hoger) beroep": {
            "subthemas": [
                "bezwaar",
                "beroep",
                "hoger beroep",
                "voorlopige voorziening",
                "schorsende werking",
                "rechterlijke toets",
                "wet dwangsommen",
                "inschakelen advocaat"
            ],
            "uitleg": "Juridische procedures voor bezwaar en beroep tegen afwijzingen of intrekkingen."
        }
    },
    "Onderwerp16": {
        "Inburgering buitenland": {
            "subthemas": ["mvv-vereiste", "verblijf bij echtgenoot", "naturalisatie"],
            "uitleg": "Procedures en voorwaarden voor inburgering en integratie van asielzoekers in het buitenland."
        },
        "Leges": {
            "subthemas": ["Legestarieven", "vrijstelling", "procedure betaling", "vergoeding", "restitutie"],
            "uitleg": "Administratieve aspecten omtrent leges en betalingsprocedures."
        }
    },
    "Onderwerp17": {
        "Middelenvereiste": {
            "subthemas": ["zelfstandig en duurzaam", "voldoen in levensonderhoud", "middelen van bestaan", "vrijstelling"],
            "uitleg": "Financiële criteria en voorwaarden voor het verkrijgen van verblijfsvergunningen."
        },
        "Mvv-vereiste": {
            "subthemas": [
                "vrijstelling",
                "mvv-procedure",
                "uitzonderingen",
                "gezondheidstoestand",
                "8 EVRM",
                "toetsingsvolgorde",
                "hardheidsclausule"
            ],
            "uitleg": "Specifieke vereisten voor de MVV-aanvraag, inclusief vrijstellingen en uitzonderingen."
        }
    },
    "Onderwerp18": {
        "Paspoortvereiste": {
            "subthemas": [
                "vrijstellingen",
                "Reguliere procedure",
                "Aanvraag mvv visumplicht",
                "D-visum",
                "TEV-procedure",
                "bestendig verblijf",
                "voorwaardes afgifte"
            ],
            "uitleg": "Juridische en administratieve vereisten voor paspoorten en visumprocedures."
        },
        "Aanvraag reguliere verblijfsvergunning": {
            "subthemas": ["aanvraag reguliere verblijfsvergunning"],
            "uitleg": "Procedure voor de aanvraag van een reguliere verblijfsvergunning."
        }
    },
    "Onderwerp19": {
        "Juridische Zaken": {
            "subthemas": ["casusanalyse", "juridisch advies", "aanvraag juridische ondersteuning"],
            "uitleg": "Ondersteuning en analyse van juridische casussen, met volledige bronvermelding volgens APA-standaard."
        },
        "Juridische Documenten en Brieven": {
            "subthemas": [
                "formele inleiding",
                "strikte juridische terminologie",
                "kopjes en onderverdelingen",
                "juridische verwijzingen",
                "bronvermelding",
                "conclusie"
            ],
            "uitleg": "Opstellen van juridische documenten en brieven conform de geldende richtlijnen."
        }
    },
    "Onderwerp20": {
        "Opvang": {
            "subthemas": [
                "opvang tijdens asielprocedure",
                "Opvangrichtlijn 2013/33/EU",
                "COa",
                "Reba",
                "Rva",
                "gezinslocatie",
                "HTL",
                "overplaatsing",
                "crisisopvang"
            ],
            "uitleg": "Procedures en maatregelen voor de opvang van asielzoekers."
        },
        "Digitale ondersteuning en registratie": {
            "subthemas": [
                "automatische opslag",
                "voortgangsmeting",
                "eindgesprek",
                "digitale registratie"
            ],
            "uitleg": "Het gebruik van digitale systemen voor registratie en opvolging van cliëntgegevens."
        }
    }
}

# ============================================================
# Functies voor Controle en Filtering van Zoekresultaten
# ============================================================

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
        if not is_relevante_bron(url):
            continue
        if not (bevat_relevante_term(titel) or bevat_relevante_term(samenvatting)):
            continue
        if not (is_gericht_op_nederland(titel) or is_gericht_op_nederland(samenvatting)):
            continue
        gefilterd.append(resultaat)
    return gefilterd

# ============================================================
# Toegevoegde Functionaliteit: Anonimisering van Gevoelige Gegevens
# ============================================================

def is_valid_bsn(bsn: str) -> bool:
    """
    Controleer of een 9-cijferig BSN voldoet aan de 11-proef.
    Indien de invoer geen 9 cijfers bevat, wordt False geretourneerd.
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
    Doorzoekt de meegegeven tekst op gevoelige gegevens: V‑nummer, BSN-nummer en namen.
    Vervangt gevonden gegevens door de placeholder [ANONIEM] en retourneert de aangepaste tekst
    samen met een lijst van meldingen.
    """
    meldingen = []

    # Controle op V‑nummer: detecteert een 'V' gevolgd door 6 tot 9 cijfers (case-insensitive).
    patroon_vnummer = re.compile(r'\bV\d{6,9}\b', re.IGNORECASE)
    if patroon_vnummer.search(invoer):
        meldingen.append("Gebruik van een V‑nummer is niet toegestaan.")
        invoer = patroon_vnummer.sub("[ANONIEM]", invoer)

    # Controle op BSN-nummer: zoek naar 8 of 9 cijferige getallen.
    patroon_bsn = re.compile(r'\b\d{8,9}\b')
    for match in patroon_bsn.findall(invoer):
        if len(match) == 9 and is_valid_bsn(match):
            meldingen.append("Gebruik van een BSN-nummer is niet toegestaan.")
            invoer = invoer.replace(match, "[ANONIEM]")
        elif len(match) == 8:
            meldingen.append("Gebruik van een BSN-nummer is niet toegestaan.")
            invoer = invoer.replace(match, "[ANONIEM]")

    # Controle op Naam: eenvoudige benadering voor twee opeenvolgende woorden die met een hoofdletter beginnen.
    patroon_naam = re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b')
    if patroon_naam.search(invoer):
        meldingen.append("Gebruik van een naam is niet toegestaan.")
        invoer = patroon_naam.sub("[ANONIEM]", invoer)

    return invoer, meldingen

def verwerk_invoer(invoer: str) -> Dict[str, Any]:
    """
    Verwerkt de invoer door eerst gevoelige gegevens te anonimiseren en vervolgens
    de aangepaste invoer te gebruiken in verdere zoek- of verwerkingsfuncties.
    Retourneert een dictionary met de geanonimiseerde invoer, meldingen en een status.
    """
    anonieme_invoer, meldingen = controleer_gevoelige_data(invoer)
    # Verdere verwerking van de (geanonimiseerde) invoer kan hier plaatsvinden.
    return {
        "geanonimiseerde_invoer": anonieme_invoer,
        "meldingen": meldingen,
        "status": "verwerking voortgezet zonder gevoelige gegevens"
    }

# ============================================================
# Overige Functionaliteit en Helper-functies
# ============================================================

def combineer_filters(data: str) -> str:
    """
    Combineert verschillende filters op de data.
    """
    # Bestaande logica om data te normaliseren of te combineren.
    return data.lower()

# ============================================================
# Main Block voor Testen
# ============================================================
if __name__ == "__main__":
    test_invoer = "De cliënt Jan Jansen heeft een V1234567 en BSN 123456782. Verder is de aanvraag compleet."
    print("Originele invoer:", test_invoer)
    resultaat = verwerk_invoer(test_invoer)
    print("Geanonimiseerde invoer:", resultaat["geanonimiseerde_invoer"])
    print("Meldingen:", resultaat["meldingen"])
