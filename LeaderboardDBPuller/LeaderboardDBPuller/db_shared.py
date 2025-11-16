import psycopg2

# Base config that is shared across all games
BASE_DB_CONFIG = {
    "host": "",
    "port": ,
    "user": "",
    "password": "",

    # SSL options (shared)
    "sslmode": "require",
    "sslrootcert": ""
}


def get_connection(dbname: str):
    """
    Return a psycopg2 connection to the given database name,
    using the shared SSL/base settings.
    """
    cfg = BASE_DB_CONFIG.copy()
    cfg["dbname"] = dbname
    return psycopg2.connect(**cfg)
