import os


def get_connection_config():
    return {
        "host": os.getenv("OLIST_DB_HOST", "localhost"),
        "port": os.getenv("OLIST_DB_PORT", "5432"),
        "dbname": os.getenv("OLIST_DB_NAME", "olist"),
        "user": os.getenv("OLIST_DB_USER", "olist_user"),
        "password": os.getenv(
            "OLIST_DB_PASSWORD",
            "olist_password",
        ),
    }