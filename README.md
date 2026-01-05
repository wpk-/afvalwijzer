# afvalwijzer
Schrijf de online afvalwijzer uit in een pdf of docx (of csv of xlsx).


## Configuratie

#### 1. Requirements
`pip install -r requirements.txt` installeert de dependencies in je python
omgeving.

#### 2. Database verbinding
Bewerk de verbindingsgegevens in `db-example.yaml` en sla op als `db.yaml`.


## Uitvoeren - A&G
Voor A&G exporteren we voor elk stadsdeel apart een docx met de regels voor
bewoners en een docx met de regels voor bedrijven.

#### 1. Verbind met VPN
Zorg dat je verbindt met de Azure VPN. Dit is nodig voor een verbinding met de
database.

#### 2. Voer `run_all.bat` uit
Dit script voert de volgende stappen uit:

1. Maakt een map aan met de huidige datum.
2. Downloadt daarin de gegevens uit de online database (duurt een paar minuten).
3. Maakt voor elk stadsdeel apart twee docx bestanden: één voor bewoners en een
   aparte voor bedrijven. (Duurt ook een paar minuten.)

Als stap 2 vandaag al is uitgevoerd wordt de bestaande download, `db.zip`,
hergebruikt. 


## Uitvoeren - app.py
Bovengenoemd script `run_all.bat` roept herhaaldelijk `app.py` aan met
verschillende argumenten. Bijvoorbeeld met de namen van de verschillende
stadsdelen.

In het algemeen is `app.py` een conversieprogramma. Het leest regels in en
schrijft regels weg -- met een keuze uit verschillende bestandsformaten en een
optie om regels te filteren.

`python app.py --help` geeft een overzicht van de mogelijkheden.

#### Bestandsformaten
De volgende bestandsformaten worden ondersteund:

| Extensie | Inhoud                                                                              | Lezen | Schrijven |
|----------|-------------------------------------------------------------------------------------|-------|-----------|
| .csv     | Kommagescheiden data in tekstbestand.                                               | ja    | ja        |
| .docx    | Opgemaakte tekst. Regels gegroepeerd per<br/> stadsdeel en afvalfractie.            | nee   | ja        |
| .pdf     | Opgemaakte tekst. Regels gegroepeerd per<br/> stadsdeel en afvalfractie. Met index. | nee   | ja        |
| .xlsx    | Spreadsheet met data.                                                               | ja    | ja        |
| .yaml    | [YAML][yaml] bestand met de verbindingsgegevens<br/> van de database.               | ja    | nee       |
| .zip     | Gecomprimeerd `.csv` bestand.                                                       | ja    | ja        |


## Licentie

[MIT](./LICENSE).


[yaml]: https://en.wikipedia.org/wiki/YAML
