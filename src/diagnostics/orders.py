import pandas as pd

from ..validation.utils import parse_timestamp


def diagnose_carrier_delivery_timestamp(orders):
    purchase_time = parse_timestamp(
        orders["order_purchase_timestamp"]
    )

    carrier_time = parse_timestamp(
        orders["order_delivered_carrier_date"]
    )

    evaluated = purchase_time.notna() & carrier_time.notna()

    invalid = evaluated & (carrier_time < purchase_time)

    return orders.loc[
        invalid,
        [
            "order_id",
            "order_purchase_timestamp",
            "order_delivered_carrier_date",
        ],
    ]