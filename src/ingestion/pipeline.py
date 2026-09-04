import uuid

from pathlib import Path

import pandas as pd

import psycopg

from ..config import get_connection_config

from ..validation.runner import run_validations, should_block

from .finalize_orders import finalize_orders

from .orders import load_orders_to_staging

from .read_staging import read_staging_orders

from .hash import calculate_file_hash


def get_connection():
    return psycopg.connect(**get_connection_config())


def create_ingestion_run(conn, ingestion_id, source_hash):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT ingestion_id, status, stage
            FROM ingestion_runs
            WHERE source_hash = %s
              AND status = 'SUCCESS'
            """,
            (source_hash,),
        )

        existing = cur.fetchone()

        if existing is not None:
            conn.rollback()

            return {
                "created": False,
                "ingestion_id": existing[0],
                "status": existing[1],
                "stage": existing[2],
            }

        cur.execute(
            """
            INSERT INTO ingestion_runs (
                ingestion_id,
                source_hash,
                status,
                stage
            )
            VALUES (%s, %s, 'RUNNING', 'STAGING')
            """,
            (ingestion_id, source_hash),
        )

    conn.commit()

    return {
        "created": True,
        "ingestion_id": ingestion_id,
        "status": "RUNNING",
        "stage": "STAGING",
    }

def update_ingestion_stage(conn, ingestion_id, stage, commit=True):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE ingestion_runs
            SET stage = %s
            WHERE ingestion_id = %s
            """,
            (stage, ingestion_id),
        )

    if commit:
        conn.commit()


def update_ingestion_status(
    conn,
    ingestion_id,
    status,
    error_message=None,
    commit=True,
):
    with conn.cursor() as cur:
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

    if commit:
        conn.commit()


def get_staging_row_count(conn, ingestion_id):
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


def ingest_orders(csv_path):
    ingestion_id = uuid.uuid4()
    source_hash = calculate_file_hash(csv_path)

    # --------------------------------------------------
    # 1. CREATE INGESTION RUN
    # --------------------------------------------------

    conn = get_connection()
    try:
        run_result = create_ingestion_run(
            conn,
            ingestion_id,
            source_hash,
        )
    finally:
        conn.close()

    if not run_result["created"]:
        return {
            "ingestion_id": run_result["ingestion_id"],
            "status": "ALREADY_PROCESSED",
            "blocking_rules": [],
        }

    try:

        # --------------------------------------------------
        # 2. LOAD INTO STAGING
        # --------------------------------------------------

        customers = pd.read_csv(
            Path(
                "Project-Data/raw/"
                "olist_customers_dataset.csv"
            )
        )

        conn = get_connection()

        try:
            load_orders_to_staging(
                csv_path,
                ingestion_id,
                conn,
            )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

        # --------------------------------------------------
        # 3. MOVE TO VALIDATION STAGE
        # --------------------------------------------------

        conn = get_connection()

        try:
            update_ingestion_stage(
                conn,
                ingestion_id,
                "VALIDATING",
            )

        finally:
            conn.close()

        # --------------------------------------------------
        # 4. READ STAGING DATA
        # --------------------------------------------------

        conn = get_connection()

        try:
            orders = read_staging_orders(
                conn,
                ingestion_id,
            )

            staged_count = get_staging_row_count(
                conn,
                ingestion_id,
            )

        finally:
            conn.close()

        # --------------------------------------------------
        # 5. VALIDATE
        # --------------------------------------------------

        results = run_validations(
            orders,
            customers,
        )

        blocking_rules = should_block(results)

        # --------------------------------------------------
        # 6. REJECT IF BLOCKING VALIDATION FAILS
        # --------------------------------------------------

        if blocking_rules:
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

        # --------------------------------------------------
        # 7. MOVE TO FINALIZATION STAGE
        # --------------------------------------------------

        conn = get_connection()

        try:
            update_ingestion_stage(
                conn,
                ingestion_id,
                "FINALIZING",
            )

        finally:
            conn.close()

        # --------------------------------------------------
        # 8. FINALIZE
        # --------------------------------------------------

        conn = get_connection()

        try:
            finalized_count = finalize_orders(
                conn,
                ingestion_id,
            )

            if staged_count != finalized_count:
                raise RuntimeError(
                    "Staging/finalization row count mismatch: "
                    f"staged={staged_count}, "
                    f"finalized={finalized_count}"
                )

            # COMPLETE + SUCCESS + finalization
            # are committed together.

            #
            # IMPORTANT:
            # update_ingestion_stage currently commits
            # automatically.
            #
            # Therefore we cannot make COMPLETE atomic
            # with finalization using the current function.
            #
            # We will fix this immediately after the
            # idempotency experiment.
            #

            update_ingestion_stage(
                conn,
                ingestion_id,
                "COMPLETE",
                commit=False,
            )

            update_ingestion_status(
                conn,
                ingestion_id,
                "SUCCESS",
                commit=False,
            )
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

        # --------------------------------------------------
        # 9. RETURN SUCCESS
        # --------------------------------------------------

        return {
            "ingestion_id": ingestion_id,
            "status": "SUCCESS",
            "blocking_rules": [],
            "staged_count": staged_count,
            "finalized_count": finalized_count,
        }

    # --------------------------------------------------
    # 10. UNEXPECTED FAILURE
    # --------------------------------------------------

    except Exception as exc:

        conn = get_connection()

        try:
            update_ingestion_stage(
                conn,
                ingestion_id,
                "INCOMPLETE",
            )

            update_ingestion_status(
                conn,
                ingestion_id,
                "FAILED",
                error_message=str(exc),
            )

        finally:
            conn.close()

        raise


if __name__ == "__main__":
    result = ingest_orders(
        Path("Project-Data/raw/olist_orders_dataset.csv")
    )
    print(result)