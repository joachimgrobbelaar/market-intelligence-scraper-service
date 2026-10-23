# market-intelligence-scraper-service

> **High-resilience Python data extraction and ETL pipeline: proxy rotation, exponential backoff, fingerprint management, stealth headers, and automated PostgreSQL/webhook delivery — uninterrupted automated market intelligence feeds.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-multi--stage-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions)](https://github.com/joachimgrobbelaar/market-intelligence-scraper-service/actions)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

---

## Problem Solved

Standard web scrapers break within hours on production targets: rotating CAPTCHAs, TLS fingerprinting, device-signature blocking, per-IP rate limits, and JavaScript-heavy SPAs that naive `requests`-based extractors cannot parse. Off-the-shelf solutions lack structured data normalization, have no audit trail, and provide no downstream delivery mechanism to databases or webhook consumers.

**market-intelligence-scraper-service** is a production-grade data extraction microservice engineered specifically to survive aggressive anti-bot environments. It implements rotating residential proxies, per-request browser fingerprint randomization, stealth HTTP headers, adaptive exponential backoff, and headless Playwright fallback for JavaScript-rendered targets — all wired into an async FastAPI job dispatcher that normalizes extracted data to PostgreSQL and fires webhook deliveries downstream.

## Architecture Overview

The service is built as an async job dispatcher. Incoming scrape requests hit a FastAPI endpoint which queues collection jobs backed by Redis. The extraction engine applies a layered anti-detection strategy: stealth headers first, proxy rotation second, exponential backoff on rate-limit signals (429/503), and headless Playwright fallback for JS-rendered targets. Extracted data is normalized via Pydantic schemas and simultaneously written to PostgreSQL and dispatched to configured webhook endpoints. A GitHub Actions CI pipeline validates the full stack on Python 3.11 and 3.12 on every push.

```mermaid
flowchart TD
    A["POST /api/v1/jobs/collect\n(target_urls, proxy_tier)"] --> B["FastAPI Job Dispatcher\n(Pydantic validation, job_id)"]
    B --> C["Redis Job Queue\n(async background task)"]
    C --> D["Extraction Engine"]
    D --> E{"Anti-Bot Strategy"}
    E -->|Attempt 1| F["Stealth Headers\n+ Rotating Proxies"]
    E -->|Rate-limited 429/503| G["Exponential Backoff\n+ Proxy Rotation"]
    E -->|JS-rendered| H["Headless Playwright\nFallback"]
    F --> I["Data Normalizer\n(Pydantic schema)"]
    G --> I
    H --> I
    I --> J["PostgreSQL Write\n(structured records)"]
    I --> K["Webhook Delivery\n(downstream consumers)"]
    J --> L["GET /api/v1/jobs/{job_id}\n(status + results)"]
```

---

## Core Engineering Features

- **Layered Anti-Detection Stack:** Requests cycle through: (1) stealth HTTP headers mimicking real browser signatures, (2) rotating residential proxy pool with per-request selection, (3) exponential backoff with jitter on `429`/`503` signals, and (4) headless Playwright fallback for JavaScript-rendered SPAs — with automatic escalation between layers.
- **Async FastAPI Job Dispatcher:** Collection jobs are dispatched as non-blocking `BackgroundTasks`, returning a `job_id` immediately. Job status and structured results are retrievable via `GET /api/v1/jobs/{job_id}` at any point during or after extraction.
- **Pydantic-Validated Data Normalization:** All extracted records are coerced through `ScrapedItem` Pydantic schemas (URL, price, currency, confidence score) before persistence, ensuring downstream data integrity regardless of source format variation.
- **PostgreSQL + Webhook Dual Delivery:** Normalized records are written to PostgreSQL for structured querying and simultaneously POSTed to configured webhook endpoints, enabling real-time feed delivery to downstream analytics pipelines, dashboards, or alerting systems.
- **Production Dockerfile + CI:** Multi-stage rootless Docker build with healthcheck. GitHub Actions CI validates the full test suite against Python 3.11 and 3.12 on every push with `docker-compose` Redis dependency.

---

## Repository Structure

```
market-intelligence-scraper-service/
├── app/
│   ├── main.py                  # FastAPI app: /health, /api/v1/jobs/collect, /api/v1/jobs/{id}
│   ├── models.py                # Pydantic schemas: ScrapeJobRequest, ScrapeJobResponse, ScrapedItem
│   └── __init__.py
├── tests/
│   └── test_api.py              # pytest TestClient: health, collect, job status, edge cases
├── docker-compose.yml           # FastAPI service + Redis dependency
├── Dockerfile                   # Multi-stage rootless build with healthcheck
├── requirements.txt
└── .github/
    └── workflows/
        └── ci.yml               # GitHub Actions: Python 3.11 & 3.12 test matrix
```

---

## Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/joachimgrobbelaar/market-intelligence-scraper-service.git
cd market-intelligence-scraper-service
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Set: DATABASE_URL, WEBHOOK_ENDPOINT, PROXY_LIST, etc.
```

### 3. Run Tests

```bash
python3 -m pytest -v tests/
```

### 4. Start Local Dev Server

```bash
uvicorn app.main:app --reload --port 8010
# Swagger docs: http://localhost:8010/docs
```

### 5. Build & Run Docker

```bash
docker-compose up --build
```

### 6. Submit a Scrape Job

```bash
curl -X POST http://localhost:8010/api/v1/jobs/collect \
  -H "Content-Type: application/json" \
  -d '{
    "target_urls": ["https://example.com/product/1", "https://example.com/product/2"],
    "proxy_tier": "rotating_residential"
  }'
# Returns: {"job_id": "job-1001", "status": "queued", "target_count": 2}
```

### 7. Retrieve Results

```bash
curl http://localhost:8010/api/v1/jobs/job-1001
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/api/v1/jobs/collect` | Submit scrape job (target_urls, proxy_tier) |
| `GET` | `/api/v1/jobs/{job_id}` | Get job status and extracted results |

---

## Environment Variables (`.env.example`)

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/market_intelligence

# Webhook delivery
WEBHOOK_ENDPOINT=https://your-downstream-service.com/ingest

# Proxy configuration
PROXY_LIST=http://proxy1:port,http://proxy2:port
PROXY_TIER=rotating_residential

# Redis
REDIS_URL=redis://localhost:6379/0
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI + Pydantic v2 |
| Extraction | `httpx` (async), Playwright (headless fallback) |
| Anti-Detection | Stealth headers, proxy rotation, exponential backoff |
| Job Queue | Redis 7 (`BackgroundTasks`) |
| Data Store | PostgreSQL 16 |
| Containerization | Docker (multi-stage, rootless) + Docker Compose |
| CI/CD | GitHub Actions (Python 3.11 & 3.12 matrix) |
| Testing | pytest + FastAPI `TestClient` |

---

## Author

**Joachim (Marnu) Grobbelaar** — AI & Python Backend Engineer  
[GitHub @joachimgrobbelaar](https://github.com/joachimgrobbelaar) · [Hugging Face @Marnu25](https://huggingface.co/Marnu25) · [LinkedIn](https://www.linkedin.com/in/joachimgrobbelaar)
