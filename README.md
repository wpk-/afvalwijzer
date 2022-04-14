# afvalwijzer
Vat de volledige Afvalwijzer samen in een enkele pdf.

## Configuratie
`pip install -r requirements.txt` installeert de dependencies in je python
omgeving.

In `config.py` staan een aantal bestandsnamen. Pas deze aan naar eigen inzicht.

In `afvalwijzer/pdf.py` staan een aantal constanten met onder andere verwijzing
naar fonts in je systeem. Pas deze aan naar je eigen systeem config. (In de
toekomst zal deze configuratie verplaatsen naar `config.py`)

## Uitvoeren
Draai eenmaal `tests.py`. Dit genereert een extract met de eerste 10.000 regels
van het databestand. Als dit succesvol draait is je setup goed.

Je kan met het test script ook een aantal tests uitvoeren om inzicht te krijgen
in de samenhang van waardes in het databestad. Zie de verscheidene `test_info_`
functies. Ze zijn redelijk goed gedocumenteerd.

Gebruik uiteindelijk `main.py` om werkelijk het ruwe databestand om te zetten
naar een overzichtelijk `.pdf` bestand. Deze staat ingesteld om te werken met
het 10k bestand. Pas onderin de commentaren aan om het uit te voeren op het
volledige databestand.

## Licentie

[MIT](./LICENSE).
