from .utils import parse_timestamp


def validate_order_customer_ids(context):
    orders = context["orders"]
    customers = context["customers"]

    valid_customer_ids = set(customers["customer_id"])

    invalid_customer_ids = ~orders["customer_id"].isin(
        valid_customer_ids
    )

    failed = int(invalid_customer_ids.sum())
    evaluated = len(orders)
    passed = evaluated - failed

    return {
        "rule": "order_customer_exists",
        "type": "referential_integrity",
        "severity": "ERROR",
        "evaluated": evaluated,
        "passed": passed,
        "failed": failed,
    }


def validate_order_id_unique(context):
    orders = context["orders"]

    duplicate_rows = orders["order_id"].duplicated(
        keep=False
    )

    failed = int(duplicate_rows.sum())
    evaluated = len(orders)
    passed = evaluated - failed

    return {
        "rule": "order_id_unique",
        "type": "structural_integrity",
        "severity": "ERROR",
        "evaluated": evaluated,
        "passed": passed,
        "failed": failed,
    }


def validate_carrier_delivery_timestamp(context):
    orders = context["orders"]

    purchase_time = parse_timestamp(
        orders["order_purchase_timestamp"]
    )

    carrier_time = parse_timestamp(
        orders["order_delivered_carrier_date"]
    )

    evaluated = purchase_time.notna() & carrier_time.notna()

    invalid = evaluated & (carrier_time < purchase_time)

    failed = int(invalid.sum())
    evaluated_count = int(evaluated.sum())
    passed = evaluated_count - failed

    return {
        "rule": "carrier_date_after_purchase",
        "type": "timestamp_anomaly",
        "severity": "WARNING",
        "evaluated": evaluated_count,
        "passed": passed,
        "failed": failed,
    }


def validate_estimated_delivery_timestamp(context):
    orders = context["orders"]

    purchase_time = parse_timestamp(
        orders["order_purchase_timestamp"]
    )

    delivery_time = parse_timestamp(
        orders["order_estimated_delivery_date"]
    )

    evaluated = purchase_time.notna() & delivery_time.notna()

    invalid = evaluated & (delivery_time < purchase_time)

    failed = int(invalid.sum())
    evaluated_count = int(evaluated.sum())
    passed = evaluated_count - failed

    return {
        "rule": "delivery_date_after_purchase",
        "type": "timestamp_anomaly",
        "severity": "WARNING",
        "evaluated": evaluated_count,
        "passed": passed,
        "failed": failed,
    }


def validate_purchase_timestamp_parseable(context):
    orders = context["orders"]

    parsed = parse_timestamp(
        orders["order_purchase_timestamp"]
    )

    evaluated = orders["order_purchase_timestamp"].notna()

    invalid = evaluated & parsed.isna()

    failed = int(invalid.sum())
    evaluated_count = int(evaluated.sum())
    passed = evaluated_count - failed

    return {
        "rule": "purchase_timestamp_parseable",
        "type": "timestamp_format",
        "severity": "ERROR",
        "evaluated": evaluated_count,
        "passed": passed,
        "failed": failed,
    }


def validate_estimated_delivery_timestamp_parseable(context):
    orders = context["orders"]

    parsed = parse_timestamp(
        orders["order_estimated_delivery_date"]
    )

    evaluated = orders["order_estimated_delivery_date"].notna()

    invalid = evaluated & parsed.isna()

    failed = int(invalid.sum())
    evaluated_count = int(evaluated.sum())
    passed = evaluated_count - failed

    return {
        "rule": "estimated_delivery_timestamp_parseable",
        "type": "timestamp_format",
        "severity": "ERROR",
        "evaluated": evaluated_count,
        "passed": passed,
        "failed": failed,
    }


def validate_required_order_fields(context):
    orders = context["orders"]

    required_columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_estimated_delivery_date",
    ]

    invalid = orders[required_columns].isna().any(axis=1)

    failed = int(invalid.sum())
    evaluated = len(orders)
    passed = evaluated - failed

    return {
        "rule": "required_order_fields_present",
        "type": "completeness",
        "severity": "ERROR",
        "evaluated": evaluated,
        "passed": passed,
        "failed": failed,
    }