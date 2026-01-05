import logging
from collections.abc import Iterable, Iterator
from pathlib import Path

from psycopg import connect, sql, Connection, OperationalError
from yaml import safe_load, dump

from afvalwijzer.models import Brongegeven

logger = logging.getLogger(__name__)

STATUS_ADRES__IN = (
    'Verblijfsobject in gebruik',
    'Plaats aangewezen',
    'Verbijfsobject in gebruik (niet ingemeten)'
)

#   Brongegeven ___________ Database (afvalwijzer_afvalwijzer)
BRON_MAP = {
    'woonfunctie':          sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('gebruiksdoel_woonfunctie'),
    'stadsdeel':            sql.Identifier('gs') + sql.SQL('.') + sql.Identifier('naam'),
    'plaatsnaam':           sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('woonplaatsnaam'),
    'buurtnaam':            sql.Identifier('gb') + sql.SQL('.') + sql.Identifier('naam'),
    'afvalfractie':         sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_fractie_naam'),
    # Verzoek van Valery om buttontekst toe te voegen. (sept 2025)
    # CONCAT('Maak een afspraak', ' ', 'of bel 14020') → 'Maak een afspraak of bel 14020'
    'instructie':           sql.SQL('CONCAT(') +
                            sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_buttontekst') +
                            sql.SQL(", ' ', ") +
                            sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_instructie_2') +
                            sql.SQL(')'),
    'ophaaldagen':          sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_ophaaldagen_2'),
    'frequentie':           sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_afvalkalender_frequentie'),
    'buitenzetten':         sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_buitenzetten'),
    'waar':                 sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_waar'),
    'opmerking':            sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_afvalkalender_opmerking'),
    'melding':              sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_afvalkalender_melding'),
    'melding_van':          sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_afvalkalender_van'),
    'melding_tot':          sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('afvalwijzer_afvalkalender_tot'),
    'straatnaam':           sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('straatnaam'),
    'huisnummer':           sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('huisnummer'),
    'huisletter':           sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('huisletter'),
    'huisnummertoevoeging': sql.Identifier('aa') + sql.SQL('.') + sql.Identifier('huisnummertoevoeging'),
}
# De volgorde van de velden is belangrijk en kan niet aangepast worden zonder
# ook het `Brongegeven` named tuple aan te passen. Dit vergt diepgaand begrip
# van de gehele code. Let op wat je doet...
assert tuple(BRON_MAP.keys()) == Brongegeven._fields


class ConnectionFailedError(OperationalError):
    """Connecting to the database failed. Most likely VPN is off."""


class TokenExpiredError(OperationalError):
    """The password token for the database connection expired."""


def read(file_in: str | Path, filters: dict[str, bool | int | str],
         ) -> Iterator[Brongegeven]:
    """Leest de Afvalwijzer regels direct uit de database.

    :param str | Path file_in: Naam van een configuratiebestand met
    verbindingsgegevens van de database.
    :param dict filters:
    :return: Een iterator over de opgevraagde brongegevens (records).
    """
    params = read_params(file_in)

    with connect_db(params) as conn:
        for record in brongegevens(conn, filters):
            yield record


def write(file_out: str | Path, data: Iterable[Brongegeven],
          filters: dict[str, bool | int | str]) -> None:
    """Schrijft de ruwe Afvalwijzer brongegevens naar de database.
    """
    raise NotImplementedError('Het is (nog) niet mogelijk om naar de database'
                              ' te schrijven.')


def brongegevens(conn: Connection,
                 filters: dict[str, bool | int | str],
                 ) -> Iterator[Brongegeven]:
    """Haalt alle brongegevens op uit de Afvalwijzer database.
    """
    query = sql.SQL('''
        SELECT {kolommen}
        FROM afvalwijzer_afvalwijzer aa
        JOIN gebieden_buurten gb ON aa.gbd_buurt_id = gb.identificatie
        JOIN gebieden_wijken gw ON gb.ligt_in_wijk_id = gw.id
        JOIN gebieden_stadsdelen gs ON gw.ligt_in_stadsdeel_id = gs.id
        WHERE aa.status_adres IN ({status})
        AND gb.eind_geldigheid IS NULL
        {filters}
        ORDER BY {kolommen}
    ''').format(
        kolommen=sql.SQL(', ').join(BRON_MAP.values()),
        status=sql.SQL(', ').join(sql.Placeholder() * len(STATUS_ADRES__IN)),
        filters=sql.SQL('').join(
            sql.SQL(' AND ') + BRON_MAP[k] + sql.SQL('=') + sql.Placeholder()
            for k in filters.keys()
        )
    )
    params = [*STATUS_ADRES__IN, *filters.values()]

    logger.debug(query.as_string())

    with conn.cursor() as cur:
        for row in cur.execute(query, params):
            yield Brongegeven(*row)


def connect_db(params: dict[str, str | int]) -> Connection:
    """Verbindt met de database of gooit informatieve foutinformatie.
    """
    try:
        return connect(f'host={params["host"]}'
                     f' port={params["port"]}'
                     f' dbname={params["dbname"]}'
                     f' user={params["user"]}'
                     f' password={params["password"]}')
    except OperationalError as err:
        msg = err.args[0]
        if (
                'token has expired' in msg or
                'is expired' in msg or
                'token has invalid' in msg or
                'new token and retry' in msg or
                'validating the access token' in msg
        ):
            raise TokenExpiredError('Het access token is verlopen.')
        elif 'getaddrinfo failed' in msg:
            raise ConnectionFailedError('Verbinding met de database is mislukt. Staat VPN aan?')
        else:
            raise err


def read_params(config_file: str | Path) -> dict[str, str | int]:
    """Leest de parameters van de databaseverbinding uit het YAML-bestand.
    """
    with open(config_file, 'r') as f:
        return safe_load(f)


def update_params(config_file: str | Path, **kwargs) -> None:
    """Werkt de parameters van de databaseverbinding bij.
    """
    logger.debug('Werk de parameters van de databaseverbinding bij...')
    params = read_params(config_file)
    params.update(kwargs)
    write_params(config_file, params)


def write_params(config_file: str | Path, params: dict[str, str | int]) -> None:
    """Schrijft de parameters van de databaseverbinding naar het YAML-bestand.
    """
    with open(config_file, 'w') as f:
        dump(params, f)
