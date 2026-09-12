import os
import secrets
import string
import tempfile
import yaml
from datetime import datetime


# ============================================================
# DATEIPFADE
# ============================================================

# Ordner, in dem dieses Python-Programm liegt
PROGRAMM_ORDNER = os.path.dirname(
    os.path.abspath(__file__)
)

# Datenordner neben dem Programm
DATEN_ORDNER = os.path.join(
    PROGRAMM_ORDNER,
    "data"
)

# Datenordner automatisch erstellen
os.makedirs(
    DATEN_ORDNER,
    exist_ok=True
)

# YAML-Datei
DATEI = os.path.join(
    DATEN_ORDNER,
    "passwords.yaml"
)


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def pause():
    input("\nDrücke Enter, um fortzufahren...")
    # Konsole leeren
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def jetzt():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ============================================================
# YAML LADEN
# ============================================================

def laden():

    if not os.path.exists(DATEI):
        return {}

    try:

        with open(
            DATEI,
            "r",
            encoding="utf-8"
        ) as datei:

            daten = yaml.safe_load(datei)

        # Leere Datei
        if daten is None:
            return {}

        # YAML muss ein Dictionary sein
        if not isinstance(daten, dict):

            print(
                "\nFehler: Die YAML-Datei "
                "hat ein ungültiges Format."
            )

            return {}

        ergebnis = {}

        for dienst, info in daten.items():

            if not isinstance(dienst, str):
                continue

            if not isinstance(info, dict):
                continue

            ergebnis[dienst] = info

        return ergebnis

    except yaml.YAMLError as fehler:

        print(
            "\nFehler beim Lesen der YAML-Datei:"
        )

        print(fehler)

        return None

    except OSError as fehler:

        print(
            "\nFehler beim Öffnen der Datei:"
        )

        print(fehler)

        return None


# ============================================================
# YAML SPEICHERN
# ============================================================

def speichern(daten):

    if daten is None:
        return False

    temp_name = None

    try:

        # Ordner sicherstellen
        os.makedirs(
            DATEN_ORDNER,
            exist_ok=True
        )

        # Zuerst temporär speichern
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=DATEN_ORDNER,
            suffix=".tmp"
        ) as temp_datei:

            yaml.safe_dump(
                daten,
                temp_datei,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False
            )

            temp_name = temp_datei.name

        # Temporäre Datei ersetzen
        os.replace(
            temp_name,
            DATEI
        )

        return True

    except OSError as fehler:

        print(
            f"\nFehler beim Speichern: {fehler}"
        )

        if (
            temp_name
            and os.path.exists(temp_name)
        ):

            try:
                os.remove(temp_name)

            except OSError:
                pass

        return False


# ============================================================
# PASSWORT GENERIEREN
# ============================================================

def passwort_generieren():

    while True:

        eingabe = input(
            "Passwortlänge "
            "(mindestens 4, Enter = 16): "
        ).strip()

        # Standardlänge
        if eingabe == "":
            laenge = 16
            break

        try:

            laenge = int(eingabe)

        except ValueError:

            print(
                "Bitte eine gültige Zahl eingeben."
            )

            continue

        if laenge < 4:

            print(
                "Das Passwort muss mindestens "
                "4 Zeichen lang sein."
            )

            continue

        if laenge > 1000:

            print(
                "Maximal 1000 Zeichen erlaubt."
            )

            continue

        break

    zeichen = (
        string.ascii_letters
        + string.digits
        + "!@#$%^&*()-_=+"
    )

    passwort = "".join(
        secrets.choice(zeichen)
        for _ in range(laenge)
    )

    print("\nGeneriertes Passwort:")
    print(passwort)

    return passwort


# ============================================================
# PASSWORT HINZUFÜGEN
# ============================================================

def hinzufuegen():

    daten = laden()

    if daten is None:
        return

    print(
        "\n=== Passwort hinzufügen ==="
    )

    # Dienst
    dienst = input(
        "Dienst/Website: "
    ).strip()

    if not dienst:

        print(
            "Der Dienst darf nicht leer sein."
        )

        return

    # Prüfen, ob Dienst schon existiert
    if dienst in daten:

        print(
            "Dieser Dienst existiert bereits."
        )

        return

    # Benutzername
    benutzername = input(
        "Benutzername: "
    ).strip()

    # Passwort
    passwort = input(
        "Passwort: "
    )

    # URL
    url = input(
        "URL: "
    ).strip()

    # Notizen
    notizen = input(
        "Notizen: "
    ).strip()

    # Eintrag erstellen
    daten[dienst] = {

        "benutzername": benutzername,

        "passwort": passwort,

        "url": url,

        "notizen": notizen,

        "erstellt": jetzt()
    }

    # Speichern
    if speichern(daten):

        print(
            "\nEintrag erfolgreich gespeichert."
        )


# ============================================================
# EINTRÄGE ANZEIGEN + AUSWÄHLEN
# ============================================================

def anzeigen():

    daten = laden()

    if daten is None:
        return

    if not daten:

        print(
            "\nKeine Einträge vorhanden."
        )

        return

    # Alphabetisch sortieren
    sortierte_dienste = sorted(
        daten.keys(),
        key=str.lower
    )

    print(
        "\n=== Gespeicherte Dienste ==="
    )

    # Nur Nummer + Dienst anzeigen
    for nummer, dienst in enumerate(
        sortierte_dienste,
        1
    ):

        print(
            f"{nummer}. {dienst}"
        )

    print()

    # Nummer auswählen
    try:

        auswahl = int(
            input(
                "Nummer des Eintrags: "
            ).strip()
        )

    except ValueError:

        print(
            "Bitte eine gültige Nummer eingeben."
        )

        return

    # Nummer prüfen
    if (
        auswahl < 1
        or auswahl > len(sortierte_dienste)
    ):

        print(
            "Diese Nummer existiert nicht."
        )

        return

    # Dienst anhand der Nummer bestimmen
    dienst = sortierte_dienste[
        auswahl - 1
    ]

    info = daten[dienst]

    # Alle Informationen anzeigen
    print(
        "\n========================================"
    )

    print(
        f"Dienst:       {dienst}"
    )

    print(
        f"Benutzername: "
        f"{info.get('benutzername', '')}"
    )

    print(
        f"Passwort:     "
        f"{info.get('passwort', '')}"
    )

    print(
        f"URL:          "
        f"{info.get('url', '')}"
    )

    print(
        f"Notizen:      "
        f"{info.get('notizen', '')}"
    )

    print(
        f"Erstellt:     "
        f"{info.get('erstellt', '')}"
    )

    print(
        f"Geändert:     "
        f"{info.get('geaendert', '-')}"
    )

    print(
        "========================================"
    )


# ============================================================
# SUCHE
# ============================================================

def suchen():

    daten = laden()

    if daten is None:
        return

    if not daten:

        print(
            "Keine Einträge vorhanden."
        )

        return

    suchbegriff = input(
        "Suchbegriff: "
    ).strip().lower()

    if not suchbegriff:

        print(
            "Suchbegriff darf nicht leer sein."
        )

        return

    treffer = []

    for dienst, info in daten.items():

        text = " ".join([
            str(dienst),

            str(
                info.get(
                    "benutzername",
                    ""
                )
            ),

            str(
                info.get(
                    "url",
                    ""
                )
            ),

            str(
                info.get(
                    "notizen",
                    ""
                )
            )
        ]).lower()

        if suchbegriff in text:

            treffer.append(
                (dienst, info)
            )

    print(
        "\n=== Suchergebnisse ==="
    )

    if not treffer:

        print(
            "Keine Treffer."
        )

        return

    treffer.sort(
        key=lambda x: x[0].lower()
    )

    for dienst, info in treffer:

        print(
            "\n----------------------------------------"
        )

        print(
            f"Dienst:       {dienst}"
        )

        print(
            f"Benutzername: "
            f"{info.get('benutzername', '')}"
        )

        print(
            f"Passwort:     "
            f"{info.get('passwort', '')}"
        )

        print(
            f"URL:          "
            f"{info.get('url', '')}"
        )

        print(
            f"Notizen:      "
            f"{info.get('notizen', '')}"
        )


# ============================================================
# EINTRAG BEARBEITEN
# ============================================================

def bearbeiten():

    daten = laden()

    if daten is None:
        return

    if not daten:

        print(
            "Keine Einträge vorhanden."
        )

        return

    print(
        "\n=== Eintrag bearbeiten ==="
    )

    # Dienste anzeigen
    sortierte_dienste = sorted(
        daten.keys(),
        key=str.lower
    )

    for nummer, dienst in enumerate(
        sortierte_dienste,
        1
    ):

        print(
            f"{nummer}. {dienst}"
        )

    print()

    try:

        auswahl = int(
            input(
                "Nummer des Eintrags: "
            ).strip()
        )

    except ValueError:

        print(
            "Bitte eine gültige Nummer eingeben."
        )

        return

    if (
        auswahl < 1
        or auswahl > len(sortierte_dienste)
    ):

        print(
            "Diese Nummer existiert nicht."
        )

        return

    dienst = sortierte_dienste[
        auswahl - 1
    ]

    info = daten[dienst]

    print(
        f"\nBearbeite: {dienst}"
    )

    print(
        "Enter = aktuellen Wert behalten"
    )

    # Benutzername
    alt = str(
        info.get(
            "benutzername",
            ""
        )
    )

    wert = input(
        f"Benutzername [{alt}]: "
    )

    if wert:
        info["benutzername"] = wert

    # Passwort
    alt = str(
        info.get(
            "passwort",
            ""
        )
    )

    wert = input(
        f"Passwort [{alt}]: "
    )

    if wert:
        info["passwort"] = wert

    # URL
    alt = str(
        info.get(
            "url",
            ""
        )
    )

    wert = input(
        f"URL [{alt}]: "
    )

    if wert:
        info["url"] = wert

    # Notizen
    alt = str(
        info.get(
            "notizen",
            ""
        )
    )

    wert = input(
        f"Notizen [{alt}]: "
    )

    if wert:
        info["notizen"] = wert

    # Änderungsdatum
    info["geaendert"] = jetzt()

    if speichern(daten):

        print(
            "\nEintrag erfolgreich aktualisiert."
        )


# ============================================================
# EINTRAG LÖSCHEN
# ============================================================

def loeschen():

    daten = laden()

    if daten is None:
        return

    if not daten:

        print(
            "Keine Einträge vorhanden."
        )

        return

    print(
        "\n=== Eintrag löschen ==="
    )

    # Dienste anzeigen
    sortierte_dienste = sorted(
        daten.keys(),
        key=str.lower
    )

    for nummer, dienst in enumerate(
        sortierte_dienste,
        1
    ):

        print(
            f"{nummer}. {dienst}"
        )

    print()

    try:

        auswahl = int(
            input(
                "Nummer des Eintrags: "
            ).strip()
        )

    except ValueError:

        print(
            "Bitte eine gültige Nummer eingeben."
        )

        return

    if (
        auswahl < 1
        or auswahl > len(sortierte_dienste)
    ):

        print(
            "Diese Nummer existiert nicht."
        )

        return

    dienst = sortierte_dienste[
        auswahl - 1
    ]

    print(
        f"\nDu möchtest "
        f"'{dienst}' löschen."
    )

    bestaetigung = input(
        "Zur Bestätigung "
        "'LOESCHEN' eingeben: "
    ).strip()

    if bestaetigung != "LOESCHEN":

        print(
            "Löschen abgebrochen."
        )

        return

    del daten[dienst]

    if speichern(daten):

        print(
            "Eintrag erfolgreich gelöscht."
        )


# ============================================================
# SPEICHERORT
# ============================================================

def speicherort():

    print(
        "\n=== Speicherort ==="
    )

    print(
        f"\nProgramm:"
        f"\n{PROGRAMM_ORDNER}"
    )

    print(
        f"\nDatenordner:"
        f"\n{DATEN_ORDNER}"
    )

    print(
        f"\nPasswortdatei:"
        f"\n{DATEI}"
    )

    print(
        "\nDie Passwörter werden "
        "unverschlüsselt gespeichert."
    )


# ============================================================
# MENÜ
# ============================================================

def main():

    while True:

        print()

        print(
            "╔════════════════════════════════════╗"
        )

        print(
            "║       PYTHON PASSWORD MANAGER      ║"
        )

        print(
            "╠════════════════════════════════════╣"
        )

        print(
            "║ 1 - Passwort hinzufügen            ║"
        )

        print(
            "║ 2 - Einträge anzeigen              ║"
        )

        print(
            "║ 3 - Suche                          ║"
        )

        print(
            "║ 4 - Eintrag bearbeiten             ║"
        )

        print(
            "║ 5 - Eintrag löschen                ║"
        )

        print(
            "║ 6 - Passwort generieren            ║"
        )

        print(
            "║ 7 - Speicherort anzeigen           ║"
        )

        print(
            "║ 0 - Beenden                        ║"
        )

        print(
            "╚════════════════════════════════════╝"
        )

        auswahl = input(
            "\nAuswahl: "
        ).strip()

        if auswahl == "1":

            hinzufuegen()
            pause()

        elif auswahl == "2":

            anzeigen()
            pause()

        elif auswahl == "3":

            suchen()
            pause()

        elif auswahl == "4":

            bearbeiten()
            pause()

        elif auswahl == "5":

            loeschen()
            pause()

        elif auswahl == "6":

            passwort_generieren()
            pause()

        elif auswahl == "7":

            speicherort()
            pause()

        elif auswahl == "0":

            print(
                "\nProgramm beendet."
            )

            break

        else:

            print(
                "\nUngültige Auswahl."
            )

            pause()


# ============================================================
# PROGRAMM STARTEN
# ============================================================

if __name__ == "__main__":
    main()
