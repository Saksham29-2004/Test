import uuid
from pathlib import Path
from datetime import datetime

import pandas as pd
import psycopg

from .generate_incremental_snapshot import generate_snapshot
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

        # --------------------------------------------------
        # 1. Check whether this source has already been
        #    successfully processed or is currently running.
        # --------------------------------------------------

        cur.execute(
            """
            SELECT
                ingestion_id,
                status,
                stage,
                heartbeat_at
            FROM ingestion_runs
            WHERE source_hash = %s
              AND status IN ('SUCCESS', 'RUNNING')
            ORDER BY
                CASE
                    WHEN status = 'SUCCESS' THEN 0
                    WHEN status = 'RUNNING' THEN 1
                END,
                started_at DESC
            LIMIT 1
            """,
            (source_hash,),
        )

        existing = cur.fetchone()

        if existing is not None:

            ingestion_id_existing = existing[0]
            status_existing = existing[1]
            stage_existing = existing[2]
            heartbeat_at = existing[3]

            # --------------------------------------------------
            # Source already successfully processed.
            # --------------------------------------------------

            if status_existing == "SUCCESS":
                conn.rollback()

                return {
                    "created": False,
                    "ingestion_id": ingestion_id_existing,
                    "status": "SUCCESS",
                    "stage": stage_existing,
                    "recover": False,
                }

            # --------------------------------------------------
            # Source is currently being processed.
            # --------------------------------------------------

            conn.rollback()

            return {
                "created": False,
                "ingestion_id": ingestion_id_existing,
                "status": "RUNNING",
                "stage": stage_existing,
                "heartbeat_at": heartbeat_at,
                "recover": False,
            }

        # --------------------------------------------------
        # 2. Nothing active/successful exists.
        #
        #    Try to create a new RUNNING ingestion.
        # --------------------------------------------------

        cur.execute(
            """
            INSERT INTO ingestion_runs (
                ingestion_id,
                source_hash,
                status,
                stage,
                heartbeat_at
            )
            VALUES (
                %s,
                %s,
                'RUNNING',
                'STAGING',
                CURRENT_TIMESTAMP
            )
            ON CONFLICT DO NOTHING
            RETURNING ingestion_id, status, stage
            """,
            (
                ingestion_id,
                source_hash,
            ),
        )

        created = cur.fetchone()

        if created is not None:

            conn.commit()

            return {
                "created": True,
                "ingestion_id": created[0],
                "status": created[1],
                "stage": created[2],
            }

        # --------------------------------------------------
        # 3. Someone else won the race between our SELECT
        #    and INSERT.
        #
        #    Find out what happened.
        # --------------------------------------------------

        cur.execute(
            """
            SELECT
                ingestion_id,
                status,
                stage,
                heartbeat_at
            FROM ingestion_runs
            WHERE source_hash = %s
              AND status IN ('SUCCESS', 'RUNNING')
            ORDER BY
                CASE
                    WHEN status = 'SUCCESS' THEN 0
                    WHEN status = 'RUNNING' THEN 1
                END,
                started_at DESC
            LIMIT 1
            """,
            (source_hash,),
        )

        existing = cur.fetchone()

    conn.rollback()

    if existing is None:
        raise RuntimeError(
            "Source hash conflict occurred but no active or successful "
            "ingestion run was found."
        )

    return {
        "created": False,
        "ingestion_id": existing[0],
        "status": existing[1],
        "stage": existing[2],
        "heartbeat_at": existing[3],
    }


def update_ingestion_stage(
    conn,
    ingestion_id,
    stage,
    commit=True,
):
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


def update_ingestion_heartbeat(conn, ingestion_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE ingestion_runs
            SET heartbeat_at = CURRENT_TIMESTAMP
            WHERE ingestion_id = %s
              AND status = 'RUNNING'
            """,
            (ingestion_id,),
        )

    conn.commit()


def try_takeover_stale_run(conn, ingestion_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE ingestion_runs
            SET heartbeat_at = CURRENT_TIMESTAMP
            WHERE ingestion_id = %s
              AND status = 'RUNNING'
              AND heartbeat_at < CURRENT_TIMESTAMP - INTERVAL '5 minutes'
            RETURNING ingestion_id, stage;
            """,
            (ingestion_id,),
        )

        row = cur.fetchone()

    if row is None:
        conn.rollback()
        return None

    conn.commit()

    return {
        "ingestion_id": row[0],
        "stage": row[1],
    }


def ingest_orders(csv_path=None):

    # --------------------------------------------------
    # 0. GET SOURCE
    # --------------------------------------------------

    if csv_path is None:
        csv_path = generate_snapshot()

    ingestion_id = uuid.uuid4()

    source_hash = calculate_file_hash(csv_path)

    # --------------------------------------------------
    # 1. CREATE INGESTION RUN
    # --------------------------------------------------

    conn = get_connection()

    try:
        run = create_ingestion_run(
            conn,
            ingestion_id,
            source_hash,
        )
    finally:
        conn.close()

    # --------------------------------------------------
    # SOURCE ALREADY EXISTS / IN PROGRESS
    # --------------------------------------------------

    recovery_stage = None

    if not run["created"]:

        # --------------------------------------------------
        # Source already successfully processed.
        # --------------------------------------------------

        if run["status"] == "SUCCESS":
            return {
                "ingestion_id": run["ingestion_id"],
                "status": "ALREADY_SUCCESSFUL",
                "blocking_rules": [],
            }

        # --------------------------------------------------
        # Source is already being processed.
        # Try to take over only if stale.
        # --------------------------------------------------

        if run["status"] == "RUNNING":

            conn = get_connection()

            try:
                takeover = try_takeover_stale_run(
                    conn,
                    run["ingestion_id"],
                )
            finally:
                conn.close()

            # --------------------------------------------------
            # Another healthy process is still working.
            # --------------------------------------------------

            if takeover is None:
                return {
                    "ingestion_id": run["ingestion_id"],
                    "status": "ALREADY_IN_PROGRESS",
                    "blocking_rules": [],
                }

            # --------------------------------------------------
            # We successfully took over the stale run.
            # --------------------------------------------------

            ingestion_id = takeover["ingestion_id"]
            recovery_stage = takeover["stage"]

            if recovery_stage is None:
                raise RuntimeError(
                    f"Cannot recover ingestion {ingestion_id}: "
                    "checkpoint stage is missing."
                )

    # --------------------------------------------------
    # New ingestion starts at STAGING.
    # --------------------------------------------------

    if run["created"]:
        recovery_stage = "STAGING"

    try:

        # --------------------------------------------------
        # Load customers used by validation.
        #
        # Customers are currently loaded into memory because
        # the validation layer expects a DataFrame.
        # --------------------------------------------------

        customers = pd.read_csv(
            Path(
                "Project-Data/raw/"
                "olist_customers_dataset.csv"
            )
        )

        # ==================================================
        # 2. LOAD INTO STAGING
        # ==================================================

        if recovery_stage == "STAGING":

            conn = get_connection()

            try:

                staged_count = load_orders_to_staging(
                    csv_path,
                    ingestion_id,
                    conn,
                )

                # --------------------------------------------------
                # STAGING + VALIDATING checkpoint are committed
                # together with the staged rows.
                #
                # Therefore:
                #
                #   STAGING
                #       => staging transaction has not yet
                #          reached the durable VALIDATING checkpoint
                #
                #   VALIDATING
                #       => staging data is durable
                # --------------------------------------------------

                update_ingestion_stage(
                    conn,
                    ingestion_id,
                    "VALIDATING",
                    commit=False,
                )
                # import time
                # print("Sleeping for 30 seconds to simulate a crash...")
                # time.sleep(30)

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE ingestion_runs
                        SET heartbeat_at = CURRENT_TIMESTAMP
                        WHERE ingestion_id = %s
                          AND status = 'RUNNING'
                        """,
                        (ingestion_id,),
                    )

                conn.commit()

            except Exception:
                conn.rollback()
                raise

            finally:
                conn.close()

        # ==================================================
        # 3. READ STAGING DATA / VALIDATE
        # ==================================================

        if recovery_stage == "FINALIZING":

            # --------------------------------------------------
            # Validation completed successfully before the
            # process crashed.
            #
            # FINALIZING is therefore a durable checkpoint.
            #
            # Do NOT read and validate again.
            # Resume directly from finalization.
            # --------------------------------------------------

            blocking_rules = []

            conn = get_connection()

            try:

                staged_count = get_staging_row_count(
                    conn,
                    ingestion_id,
                )

            finally:
                conn.close()

        else:

            # --------------------------------------------------
            # Read durable staging data.
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

            # ==================================================
            # 4. VALIDATE
            # ==================================================

            results = run_validations(
                orders,
                customers,
            )

            blocking_rules = should_block(results)

        # ==================================================
        # 5. REJECT IF BLOCKING VALIDATION FAILS
        # ==================================================

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

        # ==================================================
        # 6. MOVE TO FINALIZATION STAGE
        # ==================================================

        # --------------------------------------------------
        # If we are recovering FROM FINALIZING, the checkpoint
        # already exists. Do not rewrite it unnecessarily.
        # --------------------------------------------------

        if recovery_stage != "FINALIZING":

            conn = get_connection()

            try:

                update_ingestion_stage(
                    conn,
                    ingestion_id,
                    "FINALIZING",
                )

                update_ingestion_heartbeat(
                    conn,
                    ingestion_id,
                )

            finally:
                conn.close()

        # ==================================================
        # 7. FINALIZE
        # ==================================================

        conn = get_connection()

        try:

            inserted_count = finalize_orders(
                conn,
                ingestion_id,
            )
            # import os
            # os._exit(1)

            # --------------------------------------------------
            # IMPORTANT:
            #
            # finalize_orders(), COMPLETE and SUCCESS are all
            # committed in the SAME transaction.
            #
            # Therefore a hard crash before conn.commit()
            # causes PostgreSQL to roll back the finalization.
            # --------------------------------------------------

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

        # ==================================================
        # 8. RETURN SUCCESS
        # ==================================================

        return {
            "ingestion_id": ingestion_id,
            "status": "SUCCESS",
            "blocking_rules": blocking_rules,
            "staged_count": staged_count,
            "inserted_count": inserted_count,
        }

    # ======================================================
    # 9. UNEXPECTED FAILURE
    # ======================================================

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

    result = ingest_orders("")

    print(result)