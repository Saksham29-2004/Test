from pathlib import Path

import pandas as pd

from .pipeline import get_connection
from .read_staging import read_staging_orders
from .finalize_orders import finalize_orders
from ..validation.runner import run_validations, should_block


def get_running_ingestions(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                ingestion_id,
                stage,
                started_at
            FROM ingestion_runs
            WHERE status = 'RUNNING'
            ORDER BY started_at
            """
        )

        return cur.fetchall()


def get_ingestion_run(conn, ingestion_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                ingestion_id,
                status,
                stage,
                started_at,
                completed_at,
                error_message
            FROM ingestion_runs
            WHERE ingestion_id = %s
            """,
            (ingestion_id,),
        )

        return cur.fetchone()


def get_staging_count(conn, ingestion_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)
            FROM staging_orders
            WHERE ingestion_id = %s
            """,
            (ingestion_id,),
        )

        return cur.fetchone()[0]


def update_ingestion_stage(conn, ingestion_id, stage):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE ingestion_runs
            SET stage = %s
            WHERE ingestion_id = %s
            """,
            (
                stage,
                ingestion_id,
            ),
        )

    conn.commit()


def update_ingestion_status(
    conn,
    ingestion_id,
    status,
    error_message=None,
    stage=None,
    commit=True,
):
    with conn.cursor() as cur:

        if stage is None:
            cur.execute(
                """
                UPDATE ingestion_runs
                SET
                    status = %s,
                    completed_at = CURRENT_TIMESTAMP,
                    error_message = %s
                WHERE ingestion_id = %s
                """,
                (
                    status,
                    error_message,
                    ingestion_id,
                ),
            )

        else:
            cur.execute(
                """
                UPDATE ingestion_runs
                SET
                    status = %s,
                    stage = %s,
                    completed_at = CURRENT_TIMESTAMP,
                    error_message = %s
                WHERE ingestion_id = %s
                """,
                (
                    status,
                    stage,
                    error_message,
                    ingestion_id,
                ),
            )

    if commit:
        conn.commit()


def recover_ingestion(ingestion_id):

    # --------------------------------------------------
    # 1. READ INGESTION STATE
    # --------------------------------------------------

    conn = get_connection()

    try:
        run = get_ingestion_run(
            conn,
            ingestion_id,
        )
    finally:
        conn.close()

    if run is None:
        raise ValueError(
            f"Ingestion {ingestion_id} does not exist"
        )

    (
        run_id,
        status,
        stage,
        started_at,
        completed_at,
        error_message,
    ) = run

    if status != "RUNNING":
        raise ValueError(
            f"Ingestion {ingestion_id} is not RUNNING"
        )

    print(f"Recovering ingestion: {ingestion_id}")
    print(f"Status: {status}")
    print(f"Stage: {stage}")

    # --------------------------------------------------
    # 2. INSPECT STAGING
    # --------------------------------------------------

    conn = get_connection()

    try:
        staging_count = get_staging_count(
            conn,
            ingestion_id,
        )
    finally:
        conn.close()

    print(f"Staging rows: {staging_count}")

    # --------------------------------------------------
    # 3. RECOVER STAGING
    # --------------------------------------------------

    if stage == "STAGING":

        if staging_count == 0:
            raise RuntimeError(
                "Ingestion crashed during STAGING "
                "before staging data was committed."
            )

        print(
            "Staging data exists. "
            "Continuing to validation."
        )

        conn = get_connection()

        try:
            update_ingestion_stage(
                conn,
                ingestion_id,
                "VALIDATING",
            )
        finally:
            conn.close()

        stage = "VALIDATING"

    # --------------------------------------------------
    # 4. RECOVER VALIDATION
    # --------------------------------------------------

    if stage == "VALIDATING":

        print("Reading staged data...")

        conn = get_connection()

        try:
            orders = read_staging_orders(
                conn,
                ingestion_id,
            )
        finally:
            conn.close()

        print("Running validations...")

        customers = pd.read_csv(
            Path(
                "Project-Data/raw/"
                "olist_customers_dataset.csv"
            )
        )

        results = run_validations(
            orders,
            customers,
        )

        blocking_rules = should_block(results)

        if blocking_rules:

            print(
                "Validation failed. "
                "Rejecting ingestion."
            )

            conn = get_connection()

            try:
                update_ingestion_status(
                    conn,
                    ingestion_id,
                    "REJECTED",
                    error_message=(
                        "Blocking validation rules failed: "
                        + ", ".join(blocking_rules)
                    ),
                )
            finally:
                conn.close()

            return {
                "ingestion_id": ingestion_id,
                "status": "REJECTED",
                "blocking_rules": blocking_rules,
            }

        print(
            "Validation passed. "
            "Continuing to finalization."
        )

        conn = get_connection()

        try:
            update_ingestion_stage(
                conn,
                ingestion_id,
                "FINALIZING",
            )
        finally:
            conn.close()

        stage = "FINALIZING"

    # --------------------------------------------------
    # 5. RECOVER FINALIZATION
    # --------------------------------------------------

    if stage == "FINALIZING":

        print("Finalizing orders...")

        conn = get_connection()

        try:

            finalized_count = finalize_orders(
                conn,
                ingestion_id,
            )

            staging_count = get_staging_count(
                conn,
                ingestion_id,
            )

            if staging_count != finalized_count:
                raise RuntimeError(
                    "Staging/finalization row count mismatch: "
                    f"staged={staging_count}, "
                    f"finalized={finalized_count}"
                )

            update_ingestion_status(
                conn,
                ingestion_id,
                "SUCCESS",
                stage="COMPLETE",
                commit=False,
            )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

        print("Recovery completed successfully.")

        return {
            "ingestion_id": ingestion_id,
            "status": "SUCCESS",
            "blocking_rules": [],
            "staged_count": staging_count,
            "finalized_count": finalized_count,
        }

    raise ValueError(
        f"Unknown recovery stage: {stage}"
    )


if __name__ == "__main__":

    ingestion_id = (
        "b06a9d28-c971-4f4a-9058-965469e862fe"
    )

    result = recover_ingestion(ingestion_id)

    print(result)