# Proof-of-Concept: Automated Market Intelligence & Scraping Microservice with Anti-Detection

**Target Domain:** `market_intelligence`  
**Classification:** Enterprise Tier ($10k+) ($12,000.00 fixed)  
**Client:** QuantLeap Capital  

This repository provides an automated, production-ready Proof of Concept implementing the core architectural patterns required for this contract engagement.

---

## Architecture & Features Included
- **FastAPI Core Service** with modular Pydantic schemas and non-blocking asynchronous endpoints.
- **Resilient Verification** via Pytest test suite with TestClient.
- **Production Dockerfile** (Multi-stage build, rootless, healthcheck).
- **GitHub Actions CI Pipeline** testing across Python 3.11 and 3.12.
- **Docker Compose** configuration with Redis service dependency.

---

## Quickstart & Local Verification

### 1. Run Unit & Integration Tests
```bash
python3 -m pytest -v tests/
```

### 2. Run Local Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Open interactive Swagger documentation at `http://localhost:8000/docs`.

### 3. Build & Run Docker Container
```bash
docker build -t poc-service:latest .
docker run -p 8000:8000 poc-service:latest
```
