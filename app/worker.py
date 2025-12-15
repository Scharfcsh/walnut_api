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
        txn = Transaction(
            transaction_id=payload["transaction_id"],
            source_account=payload["source_account"],
            destination_account=payload["destination_account"],
            amount=payload["amount"],
            currency=payload["currency"],
            status="PROCESSING",
        )
        db.add(txn)
        db.commit()

    except IntegrityError:
        # Already exists → expected in retries
        db.rollback()
        txn = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == payload["transaction_id"])
            .first()
        )

    try:
        # 2️⃣ If already processed, exit
        if not txn or txn.status == "PROCESSED":
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

        # logger.info("Transaction %s processed", payload["transaction_id"])

    except Exception as e:
        # logger.error("Error processing transaction %s: %s", payload["transaction_id"], str(e))
        db.rollback()
        raise
    finally:
        db.close()
