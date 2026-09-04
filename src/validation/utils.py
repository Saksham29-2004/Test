import pandas as pd


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_timestamp(series):
    return pd.to_datetime(
        series,
        format=TIMESTAMP_FORMAT,
        errors="coerce",
    )