from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal, engine
from .models import Base, Transaction
from .schema import TransactionWebhook
from .celery import celery_app
from datetime import datetime, timezone
from .config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

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
def webhook(
    payload: TransactionWebhook,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # existing = (
    #     db.query(Transaction)
    #     .filter(Transaction.transaction_id == payload.transaction_id)
    #     .first()
    # )
    # if existing:
    #     return {"message": "Transaction already exists"}

    try:
        txn = Transaction(
            transaction_id=payload.transaction_id,
            source_account=payload.source_account,
            destination_account=payload.destination_account,
            amount=payload.amount,
            currency=payload.currency,
            status="PROCESSING",
        )
        db.add(txn)
        db.commit()

        background_tasks.add_task(
            celery_app.send_task,
            "app.tasks.process_transaction",
            args=[payload.transaction_id],
        )

    except IntegrityError:
        db.rollback()
        return {"message": "Transaction already exists"}

    return {"message": "Transaction received"}


@app.get("/v1/transactions/{transaction_id}")
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    txn = db.query(Transaction)\
            .filter(Transaction.transaction_id == transaction_id)\
            .first()

    if not txn:
        return {"error": "Not found"}

    return {
        "transaction_id": txn.transaction_id,
        "source_account": txn.source_account,
        "destination_account": txn.destination_account,
        "amount": float(txn.amount) if txn.amount is not None else None,
        "currency": txn.currency,
        "status": txn.status.value if hasattr(txn.status, 'value') else txn.status,
        "created_at": txn.created_at.isoformat().replace("+00:00", "Z") if txn.created_at else None,
        "processed_at": txn.processed_at.isoformat().replace("+00:00", "Z") if txn.processed_at else None,
    }
