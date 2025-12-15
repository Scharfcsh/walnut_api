from datetime import datetime, timezone
from sqlalchemy.orm import Session
import time
from .celery import celery_app
from .db import SessionLocal
from .models import Transaction

@celery_app.task(name="app.tasks.process_transaction")
def process_transaction(transaction_id: str):
    db: Session = SessionLocal()

    txn = db.query(Transaction)\
            .filter(Transaction.transaction_id == transaction_id)\
            .first()

    if not txn or txn.status == "PROCESSED":
        db.close()
        return

    # simulate UPI / external API
    time.sleep(30)

    txn.status = "PROCESSED"
    txn.processed_at = datetime.now(timezone.utc)

    db.commit()
    db.close()
