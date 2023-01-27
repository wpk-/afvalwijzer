# afvalwijzer
Vat de volledige Afvalwijzer samen in een enkele pdf.

## Configuratie
`pip install -r requirements.txt` installeert de dependencies in je python
omgeving.

In `afvalwijzer/pdf.py` staan een aantal constanten met onder andere verwijzing
naar fonts in je systeem. Pas deze aan naar je eigen systeem config.

## Uitvoeren
We hebben alvast een uittreksen van 1000 regels uit de afvalwijzer gedownload
naar `files/afvalwijzer-1000.csv` om mee te testen maar je kan het gemakkelijk
[zelf doen][afvalwijzer-1000-regels].

Draai `python main.py files/afvalwijzer-1000.csv output/afvalwijzer.pdf` om te
testen met de eerste 1000 regels van de afvalwijzer. Als dit succesvol draait
dan is je setup goed. Gaat er iets mis? Lees dan verder in de volgende sectie.

Gebruik uiteindelijk `main.py` om zelf gedownloade CSV bestanden te converteren
naar overzichtelijke `.pdf` bestanden. Dit verdient de aanbeveling omdat je zo
controle houdt over de gegevens in het CSV bestand.

Als alternatief is er ook `stadsdelen.py`. Dit script downloadt de CSV data van
de API zelf en maakt per stadsdeel een aparte PDF. Je hebt dus geen eigen CSV
data nodig maar let op, het downloaden van de afvalwijzer regels duurt lang.

## Problemen

Een aantal problemen zijn bekend.

### ValueError: De CSV file header wordt niet herkend.

Het is belangrijk dat het CSV bestand de juiste gegevens bevat. Voordat het
script de PDF maakt valideert het daarom eerst de input. Het kijkt naar de
eerste regel (de header) en checkt dat deze precies is zoals verwacht. Als dat
zo is, dan kloppen de kolommen en gaat het script verder. Matcht het niet, dan
geeft het deze fout.

Er worden twee regels geprint die beginnen met WARNING: De eerste toont de
header uit het input bestand, de tweede toont de header die het script verwacht
had. Je kan zo precies het verschil zien.

De fout betekent waarschijnlijk dat Datapunt de API veranderd heeft. Er is wat
programmeerwerk nodig in het bestand `afvalwijzer/models.py` om de aanpassing
van Datapunt in het script door te voeren (klasse `AfvalwijzerRegel` en
eventuele verwijzingen naar de velden.)

### Timeout

Het downloaden van de CSV data van de server duurt momenteel erg lang. Soms
zelfs zo lang dat de server (of de client) besluiten de verbinding te
verbreken. In dat geval spreken we van een timeout. De download is mislukt.

Probeer het nog een keer. Misschien heb je dit keer meer geluk. Het kan ook
helpen om de bestanden zelf met je browser te downloaden (zie boven) en
`main.py` te draaien in plaats van `stadsdelen.py`. Of vraag Datapunt om de API
te versnellen.

## Licentie

[MIT](./LICENSE).



[afvalwijzer-1000-regels]: https://api.data.amsterdam.nl/v1/afvalwijzer/afvalwijzer/?gbdBuurtCode[like]=A*&_pageSize=1000&_format=csv
