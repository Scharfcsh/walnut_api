# Walnut Transaction API

A FastAPI-based transaction processing service that meets the following requirements:

## Requirements Met ✅

1. **202 Accepted Response**: Always returns 202 status code for webhook requests
2. **Sub-500ms Response Time**: Responds immediately using Redis for idempotency and Celery for background processing  
3. **Background Processing**: Uses Celery workers to process transactions with 30-second delay simulation
4. **Idempotency**: Redis-based deduplication ensures duplicate transaction_ids are handled gracefully

## 🌐 Live Demo

**Public API Endpoint**: `https://api.amslabs.in/`

Try the live API:
```bash
curl -X POST https://api.amslabs.in/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "demo_txn_123",
    "source_account": "acc_source",
    "destination_account": "acc_dest", 
    "amount": 100.50,
    "currency": "USD"
  }'
```

**GitHub Repository**: `https://github.com/yourusername/walnut` (replace with your actual repo)

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/walnut.git
   cd walnut
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

3. **Test the webhook**:
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

4. **Check transaction status**:
   ```bash
   curl http://localhost:8000/v1/transactions/txn_123
   ```

5. **Run requirement tests**:
   ```bash
   python test_requirements.py
   ```

## 🏗️ Technical Choices

### Architecture Decisions

- **FastAPI**: Chosen for high performance, automatic OpenAPI documentation, and excellent async support
- **Redis**: Provides sub-millisecond idempotency checks and serves as Celery broker for reliability
- **Celery**: Handles background processing to meet the 500ms response requirement while simulating 30s processing
- **SQLite/PostgreSQL**: SQLite for local development, PostgreSQL for production deployment
- **Docker Compose**: Ensures consistent local development environment

### Performance Optimizations

- **Immediate 202 Response**: Webhook endpoint responds instantly after Redis idempotency check
- **Background Processing**: All heavy work happens asynchronously via Celery workers
- **Connection Pooling**: Database connections are pooled for efficiency
- **Async/Await**: FastAPI endpoints use async patterns for maximum throughput

### Reliability Features

- **Idempotency**: Redis-based duplicate detection prevents processing the same transaction twice
- **Health Checks**: Docker services include health checks for reliability
- **Graceful Shutdown**: Services handle shutdown signals properly
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes

## Testing

Run the full test suite:
```bash
# Unit tests
pytest tests/

# Performance tests  
python test_requirements.py

# Load testing (optional)
pip install locust
locust -f load_test.py
```

## Deployment

The service is deployed on Railway/Heroku/DigitalOcean with:
- Redis Cloud for production Redis
- PostgreSQL database
- Celery workers running in background
- Docker containers for consistency

## Endpoints

- `POST /v1/webhooks/transactions` - Accept transaction webhooks (202 response)
- `GET /v1/transactions/{transaction_id}` - Get transaction status
- `GET /` - Health check
- `GET /docs` - Interactive API documentation

## 📋 Requirements Verification

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| 202 Response | FastAPI returns 202 immediately | ✅ |
| Sub-500ms | Redis idempotency + async processing | ✅ |
| Background Processing | Celery workers with 30s simulation | ✅ |
| Idempotency | Redis-based duplicate detection | ✅ |
