REQUIRED_RESULT_FIELDS = {
    "rule",
    "type",
    "severity",
    "evaluated",
    "passed",
    "failed",
}


def validate_result(result):
    missing_fields = REQUIRED_RESULT_FIELDS - result.keys()

    if missing_fields:
        raise ValueError(
            f"Validation result missing fields: {missing_fields}"
        )

    if result["severity"] not in {"ERROR", "WARNING"}:
        raise ValueError(
            f"Invalid severity: {result['severity']}"
        )

    if result["evaluated"] != result["passed"] + result["failed"]:
        raise ValueError(
            "evaluated must equal passed + failed"
        )

    return result