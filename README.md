# Walnut Transaction API

A FastAPI-based transaction processing service that meets the following requirements:

## Requirements Met ✅

1. **202 Accepted Response**: Always returns 202 status code for webhook requests
2. **Sub-500ms Response Time**: Responds immediately using Redis for idempotency and Celery for background processing  
3. **Background Processing**: Uses Celery workers to process transactions with 30-second delay simulation
4. **Idempotency**: Redis-based deduplication ensures duplicate transaction_ids are handled gracefully

## Quick Start

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Test the webhook**:
   ```bash
   curl -X POST http://localhost:8000/v1/webhooks/transactions \
     -H "Content-Type: application/json" \
     -d '{
       "transaction_id": "txn_123",
       "source_account": "acc_source",
       "destination_account": "acc_dest", 
       "amount": 100.50,
       "currency": "USD"
     }'
   ```

3. **Check transaction status**:
   ```bash
   curl http://localhost:8000/v1/transactions/txn_123
   ```

4. **Run requirement tests**:
   ```bash
   python test_requirements.py
   ```

## Architecture

- **FastAPI**: Web framework providing the webhook endpoint
- **Redis**: Idempotency checking and Celery broker
- **Celery**: Background task processing
- **SQLite/PostgreSQL**: Transaction persistence
- **Docker Compose**: Orchestration

## Endpoints

- `POST /v1/webhooks/transactions` - Accept transaction webhooks (202 response)
- `GET /v1/transactions/{transaction_id}` - Get transaction status
- `GET /` - Health check
