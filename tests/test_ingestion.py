from src.validation.runner import should_block


def test_error_with_failure_blocks():
    results = [
        {
            "rule": "order_customer_exists",
            "type": "referential_integrity",
            "severity": "ERROR",
            "evaluated": 100,
            "passed": 99,
            "failed": 1,
        }
    ]

    assert should_block(results) == [
        "order_customer_exists"
    ]


def test_warning_with_failure_does_not_block():
    results = [
        {
            "rule": "carrier_date_after_purchase",
            "type": "timestamp_anomaly",
            "severity": "WARNING",
            "evaluated": 100,
            "passed": 90,
            "failed": 10,
        }
    ]

    assert should_block(results) == []


def test_no_failures_does_not_block():
    results = [
        {
            "rule": "order_id_unique",
            "type": "structural_integrity",
            "severity": "ERROR",
            "evaluated": 100,
            "passed": 100,
            "failed": 0,
        }
    ]

    assert should_block(results) == []


def test_multiple_errors_return_all_blocking_rules():
    results = [
        {
            "rule": "order_customer_exists",
            "type": "referential_integrity",
            "severity": "ERROR",
            "evaluated": 100,
            "passed": 99,
            "failed": 1,
        },
        {
            "rule": "order_id_unique",
            "type": "structural_integrity",
            "severity": "ERROR",
            "evaluated": 100,
            "passed": 98,
            "failed": 2,
        },
        {
            "rule": "carrier_date_after_purchase",
            "type": "timestamp_anomaly",
            "severity": "WARNING",
            "evaluated": 100,
            "passed": 90,
            "failed": 10,
        },
    ]

    assert should_block(results) == [
        "order_customer_exists",
        "order_id_unique",
    ]