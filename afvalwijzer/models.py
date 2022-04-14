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
    bag_nummeraanduiding_id: str
    afvalwijzer_id: str
    naam_openbareruimte: str
    huisnummer: str
    huisletter: str
    huisnummertoevoeging: str
    postcode: str
    woonplaatsnaam: str
    status_adres: str
    afvalwijzer_gebruiksdoel_woonfunctie: str
    afvalwijzer_instructie: str
    afvalwijzer_basisroutetype_id: str
    afvalwijzer_routenaam: str
    afvalwijzer_per_x_weken: str
    afvalwijzer_buitenzetten_vanaf_tot: str
    afvalwijzer_buitenzetten_vanaf: str
    afvalwijzer_buitenzetten_tot: str
    afvalwijzer_afvalkalender_opmerking: str
    afvalwijzer_afvalkalender_frequentie: str
    afvalwijzer_fractie_naam: str
    afvalwijzer_fractie_code: str
    afvalwijzer_routetype_naam: str
    afvalwijzer_ophaaldagen: str
    afvalwijzer_afvalkalender_melding: str
    afvalwijzer_afvalkalender_van: str
    afvalwijzer_afvalkalender_tot: str
    gbd_buurt_code: str
    gbd_buurt_id: str
    afvalwijzer_basisroutetype: str
    afvalwijzer_basisroutetype_omschrijving: str
    afvalwijzer_basisroutetype_code: str
    afvalwijzer_instructie2: str
    afvalwijzer_ophaaldagen2: str
    afvalwijzer_waar: str
    afvalwijzer_buitenzetten: str
    afvalwijzer_buttontekst: str
    lat: str
    lon: str
    afvalwijzer_url: str

    def adres(self) -> 'Adres':
        """Mapping naar adres: Amsterdam, A00c, Nieuwmarkt 4A-3."""
        woonplaats = self.woonplaatsnaam
        buurt = self.gbd_buurt_code
        straatnaam = self.naam_openbareruimte
        huisnummer = int(self.huisnummer)
        toevoeging = self.huisletter + ('-' + self.huisnummertoevoeging
                                        if self.huisnummertoevoeging else '')
        return Adres(woonplaats, buurt, straatnaam, huisnummer, toevoeging)

    def regel(self) -> 'Regel':
        """Mapping naar regel.

        Een regel heeft ook een woonplaats en buurt omdat in de PDF
        regels per buurt gepresenteerd worden.
        """
        return Regel(
            self.woonplaatsnaam,
            self.gbd_buurt_code,
            self.afvalwijzer_fractie_naam,
            self.afvalwijzer_afvalkalender_melding,
            self.afvalwijzer_afvalkalender_van,
            self.afvalwijzer_afvalkalender_tot,
            self.afvalwijzer_instructie2,
            self.afvalwijzer_ophaaldagen2,
            self.afvalwijzer_afvalkalender_frequentie,
            self.afvalwijzer_buitenzetten,
            self.afvalwijzer_waar,
            self.afvalwijzer_afvalkalender_opmerking,
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
