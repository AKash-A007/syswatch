# 📊 Monitoring Setup Guide

This guide walks you through connecting SysWatch Pro's backend to free monitoring services.

---

## 1. UptimeRobot — Uptime Monitoring (Free)

**What it does:** Pings your `/health` endpoint every 5 minutes and alerts you via email/SMS/Slack if it goes down.

### Steps

1. Go to [uptimerobot.com](https://uptimerobot.com) → Sign up (free)
2. Click **"+ Add New Monitor"**
3. Fill in:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** `SysWatch Pro API`
   - **URL:** `https://syswatch.onrender.com/health`
   - **Monitoring Interval:** 5 minutes
4. Add alert contacts (email is free)
5. Click **"Create Monitor"**

### Add status badge to README

```markdown
[![Uptime Robot status](https://img.shields.io/uptimerobot/status/m<YOUR_MONITOR_ID>?label=API%20Uptime)](https://stats.uptimerobot.com/<YOUR_STATUS_PAGE>)
```

---

## 2. Sentry — Error Tracking (Free tier: 5K errors/month)

**What it does:** Captures exceptions in production with full stack traces, breadcrumbs, and context.

### Installation

Add to `requirements.txt`:
```
sentry-sdk[fastapi]==2.3.1
```

### Integration in FastAPI (`src/backend/api_server.py`)

Add this near the top of your FastAPI app initialization:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", ""),   # Set via env var — never hardcode!
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
    traces_sample_rate=0.1,    # 10% of requests traced (free tier friendly)
    profiles_sample_rate=0.1,
    environment=os.getenv("PYTHON_ENV", "development"),
    release=os.getenv("APP_VERSION", "unknown"),
)
```

### Setup

1. Go to [sentry.io](https://sentry.io) → Sign up with GitHub
2. Create a new project → Select **Python** → **FastAPI**
3. Copy your **DSN**
4. Add as GitHub secret: `SENTRY_DSN`
5. Add to Render env var: `SENTRY_DSN = <your-dsn>`

---

## 3. Grafana Cloud — Metrics Dashboard (Free: 10K series)

**What it does:** Prometheus-compatible metrics dashboard — CPU, request rate, latency histograms.

### Installation

Add to `requirements.txt`:
```
prometheus-fastapi-instrumentator==6.1.0
```

### Integration in FastAPI

```python
from prometheus_fastapi_instrumentator import Instrumentator

# After creating app = FastAPI(...)
Instrumentator().instrument(app).expose(app)
# Exposes metrics at GET /metrics (Prometheus format)
```

### Setup

1. Go to [grafana.com/grafana/cloud](https://grafana.com/grafana/cloud) → Sign up free
2. Go to **Connections → Add new connection → Prometheus**
3. Install **Grafana Agent** on your server OR use the remote_write config:

```yaml
# Add to your deployment environment
metrics:
  global:
    scrape_interval: 15s
  configs:
    - name: syswatch
      scrape_configs:
        - job_name: syswatch-api
          static_configs:
            - targets: ['syswatch.onrender.com:443']
          scheme: https
          metrics_path: /metrics
      remote_write:
        - url: https://prometheus-prod-<id>.grafana.net/api/prom/push
          basic_auth:
            username: <your-grafana-username>
            password: <your-grafana-api-key>
```

4. Import dashboard template ID **`11074`** (FastAPI default) in Grafana

---

## 4. GitHub Actions Summary

| Service | Free Tier | What You Get |
|---------|-----------|-------------|
| UptimeRobot | ✅ Forever free | 50 monitors, 5-min checks, email alerts |
| Sentry | ✅ 5K events/month | Error tracking, stack traces, releases |
| Grafana Cloud | ✅ 10K series | Metrics dashboards, alerting |
| Codecov | ✅ Public repos | Coverage reports on PRs |
| SonarCloud | ✅ Public repos | Code quality gate |
| Snyk | ✅ 200 tests/month | Dependency vulnerability scans |

---

## 5. GitHub Secrets to Add

Go to your repo → **Settings → Secrets and variables → Actions** → **New repository secret**:

| Secret Name | Value | Used By |
|-------------|-------|---------|
| `CODECOV_TOKEN` | From codecov.io | CI coverage upload |
| `SNYK_TOKEN` | From snyk.io | Security scan |
| `SENTRY_DSN` | From sentry.io | Error tracking |
| `RENDER_API_KEY` | From render.com | CD deploy trigger |
| `RENDER_STAGING_SERVICE_ID` | From Render dashboard | CD staging deploy |
| `RENDER_PROD_SERVICE_ID` | From Render dashboard | CD production deploy |
