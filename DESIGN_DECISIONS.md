D-001: Source Record Freshness

Decision:
Only update an existing final record when the incoming source
record can be proven to be newer.

Current limitation:
Olist provides no source-side update/version timestamp.

Current implementation:
Incoming records are treated as authoritative.

Risk:
A late-arriving stale record can overwrite newer data.

Reversal condition:
Introduce source-version/update-time comparison when the
upstream source provides such metadata.
