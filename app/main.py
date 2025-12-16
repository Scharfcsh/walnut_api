from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal, engine
from .models import Base, Transaction
from .schema import TransactionWebhook
from .celery import celery_app
from datetime import datetime, timezone
from .config import settings
import redis
import logging

logger = logging.getLogger(__name__)


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

redis_client = redis.Redis.from_url(settings.redis_url)
IDEMPOTENCY_TTL = 3600


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health():
    return {
        "status": "HEALTHY",
        "current_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

# @app.post("/v1/webhooks/transactions", status_code=202)
# def webhook(payload: TransactionWebhook, db: Session = Depends(get_db)):
#     # If a transaction with the same id already exists, do nothing and return 202
#     existing = db.query(Transaction)\
#                  .filter(Transaction.transaction_id == payload.transaction_id)\
#                  .first()
#     if existing:
#         return {"message": "Transaction already exists"}

#     try:
#         txn = Transaction(
#             transaction_id=payload.transaction_id,
#             source_account=payload.source_account,
#             destination_account=payload.destination_account,
#             amount=payload.amount,
#             currency=payload.currency,
#             status="PROCESSING",
#         )
#         db.add(txn)
#         db.commit()

#         # enqueue ONLY on first insert
#         celery_app.send_task(
#             "app.tasks.process_transaction",
#             args=[payload.transaction_id]
#         )

#     except IntegrityError:
#         db.rollback()
#         # On integrity error, do nothing further per requirements and return 202
#         return {"message": "Transaction already exists"}

#     return {"message": "Transaction received"}

@app.post("/v1/webhooks/transactions", status_code=202)
def webhook(payload: TransactionWebhook):
    try:
        key = f"txn:{payload.transaction_id}"

    
        inserted = redis_client.set(
            key,
            "1",
            nx=True,
            ex=IDEMPOTENCY_TTL,  
        )

        if not inserted:
            # logger.info("Duplicate transaction received: %s", payload.transaction_id)
            return {"message": "Transaction already exists"}

        celery_app.send_task(
            "app.tasks.process_transaction",
            args=[payload.model_dump()],
        )

        # logger.info("Transaction %s queued for processing", payload.transaction_id)
        return {"message": "Transaction received"}

    except Exception as e:
        # logger.error("Error processing webhook: %s", str(e))
        # raise HTTPException(status_code=202, detail="Internal server error")
        return {"message": "Transaction received but error"}


@app.get("/v1/transactions/{transaction_id}")
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    # Always return 2XX, provide informative messages in body
    if not transaction_id or not transaction_id.strip():
        return {"message": "Invalid transaction_id", "transaction_id": transaction_id}

    try:
        txn = db.query(Transaction)\
                .filter(Transaction.transaction_id == transaction_id)\
                .first()

        if not txn:
            return {"message": "Transaction not found", "transaction_id": transaction_id}

        return [{
            "transaction_id": txn.transaction_id,
            "source_account": txn.source_account,
            "destination_account": txn.destination_account,
            "amount": float(txn.amount) if txn.amount is not None else None,
            "currency": txn.currency,
            "status": txn.status.value if hasattr(txn.status, 'value') else txn.status,
            "created_at": txn.created_at.isoformat().replace("+00:00", "Z") if txn.created_at else None,
            "processed_at": txn.processed_at.isoformat().replace("+00:00", "Z") if txn.processed_at else None,
        }]
    except Exception as e:
        logger.exception("Error fetching transaction %s: %s", transaction_id, str(e))
        return {"message": "Internal server error", "transaction_id": transaction_id}
