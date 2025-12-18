from datetime import datetime, timezone
import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from celery.utils.log import get_task_logger

from .celery import celery_app
from .db import SessionLocal
from .models import Transaction
from .schema import TransactionWebhook

logger = get_task_logger(__name__)


@celery_app.task(
    name="app.tasks.process_transaction",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 5},
)
def process_transaction(self, payload: dict):

    db: Session = SessionLocal()

    try:
        txn = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == payload["transaction_id"])
            .first()
        )
        if not txn:
            logger.warning(
                "Transaction %s not found, skipping",
                payload["transaction_id"],
            )
            return

        if txn.status == "PROCESSED":
            return

        db.expunge(txn)   # detach object
        db.close()

        time.sleep(30)

        db = SessionLocal()
        txn = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == payload["transaction_id"])
            .with_for_update()
            .first()
        )

        if txn and txn.status != "PROCESSED":
            txn.status = "PROCESSED"
            txn.processed_at = datetime.now(timezone.utc)
            db.commit()

        logger.info("Transaction %s processed", payload["transaction_id"])

    except Exception as e:
        # logger.error("Error processing transaction %s: %s", payload["transaction_id"], str(e))
        db.rollback()
        raise
    finally:
        db.close()
