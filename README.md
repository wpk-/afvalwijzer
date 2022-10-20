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
Draai `python main.py files/afvalwijzer-1000.csv output/afvalwijzer.pdf` om te
je set-up te testen met de eerste 10.000 regels van de afvalwijzer. Als dit
succesvol draait dan is je setup goed.

Gebruik uiteindelijk `main.py` op zelf gedownloade CSV bestanden om deze om te
zetten naar overzichtelijke `.pdf` bestanden. Dit verdient de aanbeveling omdat
je zo controle houdt over de gegevens in het CSV bestand.

Als alternatief is er ook `stadsdelen.py`. Dit script maakt voor elk stadsdeel
een aparte PDF op basis van gedownloade data. Je hebt dus geen eigen CSV data
nodig. Let op, het downloaden van de afvalwijzer regels duurt lang.

## Licentie

[MIT](./LICENSE).
