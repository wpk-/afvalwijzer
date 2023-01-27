from typing import NamedTuple

import bleach

# Nodig om melding en opmerking op te schonen in `Regel.labels()`.
strip_tags = bleach.Cleaner([], {}, strip=True).clean


class AfvalwijzerRegel(NamedTuple):
    """Instructies voor een afvalfractie op een adres.

    De veldnamen komen exact en op volgorde overeen met de kolomnamen van
    de CSV data dump.

    Elke regel (instantie van deze klasse) linkt een adres aan een regel
    (=instructie). De klasse heeft daarom twee methodes:
        adres() - geeft het adres,
        regel() - geeft de regel die geldt voor het aanbieden van afval.
    """
    Id: str
    Straatnaam: str
    Huisnummer: str
    Huisletter: str
    Huisnummertoevoeging: str
    Postcode: str
    Woonplaatsnaam: str
    Statusadres: str
    Gebruiksdoelwoonfunctie: str
    Afvalwijzerinstructie: str
    Afvalwijzerbasisroutetypeid: str
    Afvalwijzerroutenaam: str
    Afvalwijzerperxweken: str
    Afvalwijzerbuitenzettenvanaftot: str
    Afvalwijzerbuitenzettenvanaf: str
    Afvalwijzerbuitenzettentot: str
    Afvalwijzerafvalkalenderopmerking: str
    Afvalwijzerafvalkalenderfrequentie: str
    Afvalwijzerfractienaam: str
    Afvalwijzerfractiecode: str
    Afvalwijzerroutetypenaam: str
    Afvalwijzerophaaldagen: str
    Afvalwijzerafvalkalendermelding: str
    Afvalwijzerafvalkalendervan: str
    Afvalwijzerafvalkalendertot: str
    Afvalwijzerbasisroutetype: str
    Afvalwijzerbasisroutetypeomschrijving: str
    Afvalwijzerbasisroutetypecode: str
    Afvalwijzergeometrie: str
    Afvalwijzerinstructie2: str
    Afvalwijzerophaaldagen2: str
    Afvalwijzerwaar: str
    Afvalwijzerbuitenzetten: str
    Afvalwijzerbuttontekst: str
    Afvalwijzerurl: str
    Bagnummeraanduidingid: str
    Gbdbuurtid: str
    Gbdbuurtcode: str
    Afvalwijzerinzamelgebiednaam: str
    Afvalwijzerinzamelgebiedcode: str

    def adres(self) -> 'Adres':
        """Mapping naar adres: Amsterdam, A00c, Nieuwmarkt 4A-3."""
        woonplaats = self.Woonplaatsnaam
        buurt = self.Gbdbuurtcode
        straatnaam = self.Straatnaam
        huisnummer = int(self.Huisnummer)
        toevoeging = self.Huisletter + ('-' + self.Huisnummertoevoeging
                                        if self.Huisnummertoevoeging else '')
        return Adres(woonplaats, buurt, straatnaam, huisnummer, toevoeging)

    def regel(self) -> 'Regel':
        """Mapping naar regel.

        Een regel heeft ook een woonplaats en buurt omdat in de PDF
        regels per buurt gepresenteerd worden.
        """
        return Regel(
            self.Woonplaatsnaam,
            self.Gbdbuurtcode,
            self.Afvalwijzerfractienaam,
            self.Afvalwijzerafvalkalendermelding,
            self.Afvalwijzerafvalkalendervan,
            self.Afvalwijzerafvalkalendertot,
            self.Afvalwijzerinstructie2,
            self.Afvalwijzerophaaldagen2,
            self.Afvalwijzerafvalkalenderfrequentie,
            self.Afvalwijzerbuitenzetten,
            self.Afvalwijzerwaar,
            self.Afvalwijzerafvalkalenderopmerking,
        )


class Adres(NamedTuple):
    """Een adres opgebouwd in volgorde van specificiteit, incl. buurt.

    Bijvoorbeeld "Amsterdam, A00c, Nieuwmarkt 4A-3"
    """
    woonplaats: str
    buurt: str
    straatnaam: str
    huisnummer: int
    toevoeging: str


class Huisnummer(NamedTuple):
    """Een volledig huisnummer, inclusief huisnummertoevoeging.

    Deze representatie wordt gebruikt om adresreeksen te maken. Binnen
    een straat worden dan opeenvolgende huisnummers samengevoegd. Op het
    laatste huisnummer wordt de toevoeging dan vervangen door een
    aanduiding voor de reeks, zoals "A--468L".
    """
    huisnummer: int
    toevoeging: str


class Straat(NamedTuple):
    """De aanduiding van een adres tot op straatniveau zonder huisnummer.
    """
    woonplaats: str
    buurt: str
    straatnaam: str


class Regel(NamedTuple):
    """De geldende regel voor het aanbieden van afval van een fractie.

    Bijvoorbeeld, hoe biedt ik mijn papier afval aan? Op welke dagen
    wordt dat ingezameld?
    """
    woonplaats: str
    buurt: str
    fractie: str
    melding: str        # = Let op
    melding_van: str    # = Let op
    melding_tot: str    # = Let op
    instructie: str     # = Hoe
    ophaaldagen: str    # = Ophaaldag
    frequentie: str     # = Ophaaldag
    buitenzetten: str   # = Buiten zetten
    waar: str           # = Waar
    opmerking: str      # = Opmerking

    def labels(self) -> list[tuple[str, str]]:
        def datum(s: str) -> str:
            """Haalt de datum uit de UTC-string."""
            return f'{s[8:10]}-{s[5:7]}-{s[0:4]}'

        arr = []

        if self.melding:
            if self.melding_van:
                arr.append(('Let op:', f'Van {datum(self.melding_van)}'
                                       f' tot {datum(self.melding_tot)}'))
                arr.append(('', strip_tags(self.melding)))
            else:
                arr.append(('Let op:', self.melding))
        if self.instructie:
            arr.append(('Hoe:', self.instructie))
        if self.ophaaldagen:
            arr.append(('Ophaaldag:', self.ophaaldagen +
                        (f', {self.frequentie}' if self.frequentie else '')))
        if self.buitenzetten:
            arr.append(('Buiten zetten:', self.buitenzetten))
        if self.waar:
            arr.append(('Waar:', self.waar))
        if self.opmerking:
            arr.append(('Opmerking:', strip_tags(self.opmerking)))

        return arr


Regelset = tuple[Regel, ...]
