CREATE TABLE ingestion_runs (
    ingestion_id UUID PRIMARY KEY,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT NOT NULL,
    error_message TEXT
);