from typing import NamedTuple, List, Tuple


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
        """Mapping naar regel."""
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
    """
    Amsterdam
    A00c
    Nieuwmarkt 4A-3
    """
    woonplaats: str
    buurt: str
    straatnaam: str
    huisnummer: int
    toevoeging: str


class Regel(NamedTuple):
    """
    Een regel geldt voor een bepaalde afvalfractie (bijv. restafval). We
    voegen ook woonplaats en buurt toe om adressen met dezelfde regels,
    maar in verschillende buurten, uit elkaar te kunnen trekken. Voor het
    sorteren is ook van belang dat woonplaats, buurt en fractie---in die
    volgorde---de eerste velden zijn.

    Restafval
    Let op:         van 31-8-2021 tot 31-8-2022
                    Breng uw kerstboom naar het inzamelpunt in uw buurt.
    Hoe:            In de container voor restafval
    Ophaaldag:      maandag, dinsdag, ..., 1e dinsdag van de maand.
    Buiten zetten:  Woensdag vanaf 21.00 tot Donderdag 07.00
    Waar:           Kaart met containers in de buurt
    Opmerking:      In Nieuw-West moet u uw tuinafval apart aanmelden.
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


class AdresRegels(NamedTuple):
    """Koppelt een verzameling adressen aan een verzameling regels.
    Deze exacte combinatie van regels geldt precies op al deze adressen.
    """
    adressen: List[Adres]
    regels: Tuple[Regel, ...]


class BuurtRegels(NamedTuple):
    """Groepeert AdresRegels per buurt."""
    buurt: Tuple[str, str]
    regels: List[AdresRegels]