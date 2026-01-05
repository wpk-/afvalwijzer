from json import loads
from subprocess import run


def get_access_token() -> str:
    """Haalt een access token op voor de verbinding met de Postgres database.
    """
    res = run(
        ['az', 'account', 'get-access-token', '--resource-type', 'oss-rdbms'],
        shell=True, capture_output=True)

    if res.returncode:
        raise OSError(res.stderr)

    return loads(res.stdout)['accessToken']
