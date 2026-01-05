from typing import NamedTuple


class Brongegeven(NamedTuple):
    """Instructies voor een afvalfractie op een adres.

    Elk brondata record koppelt 1) een adres aan 2) een geldende regel.
    Op een adres kunnen meerdere regels gelden. Dat betekent meerdere records.
    Een regel kan op meerdere adressen gelden. Ook dat betekent meerdere records.

    De volgorde van deze velden is belangrijk. Door de volgorde te veranderen
    zullen bepaalde delen van de code niet (juist) meer functioneren.
    (Zie met name `db.py` en `content.py`, maar andere delen kunnen hier ook van
    afhangen.)
    """
    # Filters
    woonfunctie: bool
    stadsdeel: str

    # (Hoofdstuk in pdf en docx)
    plaatsnaam: str
    buurtnaam: str
    afvalfractie: str

    # Regel
    instructie: str | None
    ophaaldagen: str | None
    frequentie: str | None
    buitenzetten: str | None
    waar: str | None
    opmerking: str | None
    melding: str | None
    melding_van: str | None
    melding_tot: str | None

    # Adres
    straatnaam: str
    huisnummer: int
    huisletter: str | None
    huisnummertoevoeging: str | None

    @property
    def adres(self) -> 'Adres':
        """Beschrijft puur het adres zonder buurt, fractie of afvalregels.
        """
        if self.huisnummertoevoeging:
            return Adres(self.straatnaam, self.huisnummer,
                         f'{self.huisletter}-{self.huisnummertoevoeging}')
        else:
            return Adres(self.straatnaam, self.huisnummer, self.huisletter)

    @property
    def buurt(self) -> 'Buurt':
        return Buurt(self.plaatsnaam, self.buurtnaam)

    @property
    def regel(self) -> 'Regel':
        """Beschrijft puur de afvalregel zonder buurt, fractie of adres.
        """
        return Regel(
            self.instructie,
            self.ophaaldagen,
            self.frequentie,
            self.buitenzetten,
            self.waar,
            self.opmerking,
            self.melding,
            self.melding_van,
            self.melding_tot,
        )


class Adres(NamedTuple):
    """Alleen de noodzakelijke adresgegevens.

    Plaatsnaam en buurt worden al gelezen uit het brongegeven dus alleen
    straatnaam en nummer zijn dan nog nodig. Toevoeging is een samenstelling van
    huisletter en huisnummertoevoeging.
    """
    straatnaam: str
    huisnummer: int
    toevoeging: str


class Buurt(NamedTuple):
    plaatsnaam: str
    buurtnaam: str


class Regel(NamedTuple):
    """De geldende regel voor het aanbieden van afval.

    Bijvoorbeeld, waar bied ik mijn afval aan? Op welke dagen wordt dat
    ingezameld?

    De regel beschrijft _niet_ de afvalfractie of het adres.
    """
    instructie: str | None      # = Hoe
    ophaaldagen: str | None     # = Ophaaldag
    frequentie: str | None      # = Ophaaldag
    buitenzetten: str | None    # = Buiten zetten
    waar: str | None            # = Waar
    opmerking: str | None       # = Opmerking
    melding: str | None         # = Let op
    melding_van: str | None     # = Let op
    melding_tot: str | None     # = Let op
