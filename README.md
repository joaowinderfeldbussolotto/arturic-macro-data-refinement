# Macro Data Refinement — Arturic Industries

Q4 2025 data validation pipeline for the Macro Data Refinement division.

## Final Output Metric

| Metric | Value | How it was derived |
|---|---:|---|
| Final output count | **954,665.39** | [Methodology](docs/methodology.md) |

Notebook walkthrough for the access-code investigation: [notebooks/crack_compliance.ipynb](notebooks/crack_compliance.ipynb)

## Project Structure

```
macro-data-refinement/
├── src/
│   └── app/
│       ├── main.py                       # Thin FastAPI entrypoint
│       ├── core/
│       │   ├── config.py                 # Validation constants
│       │   ├── models.py                 # Pydantic domain models
│       │   └── pipeline.py               # Pipeline state manager
│       ├── services/
│       │   ├── ingester.py               # Loads .mdr/.json, .csv, and .txt sessions
│       │   └── validator.py              # Applies all 12 compliance rules
│       └── api/
│           └── v1/
│               ├── router.py             # API v1 router aggregator
│               └── endpoints/
│                   ├── pipeline.py       # health/report/result routes
│                   └── sessions.py       # sessions routes
├── data/                                 # Quarterly output files (MDR, SA, WB)
├── docs/
│   ├── methodology.md
│   └── images/
│       └── facility_exterior.png
├── notebooks/
│   └── crack_compliance.ipynb   # Access code investigation
├── scripts/
│   └── run_pipeline.py          # Standalone CLI runner
├── tests/
│   └── test_validator.py        # 27 unit tests, one per rule / edge case
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Running with Docker

```bash
docker compose up --build
```

The `data/` directory is mounted read-only into the container.  
The API will be available at `http://localhost:8000`.

## Running locally

```bash
pip install -r requirements.txt
PYTHONPATH=src uvicorn app.main:app --reload
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/result` | Final output metric + headline counts |
| GET | `/api/v1/report` | Full report — summary + all session results |
| GET | `/api/v1/sessions` | List sessions (`?department=MDR`, `?valid_only=true`) |
| GET | `/api/v1/sessions/{id}` | Single session result |

Interactive docs: `http://localhost:8000/docs`

## CLI

```bash
python -m scripts.run_pipeline             # summary report
python -m scripts.run_pipeline --verbose   # include per-session breakdown
python -m scripts.run_pipeline --sessions data
```

## Tests

```bash
python -m pytest tests/ -v
```

## Validation rules

| # | Rule | Source |
|---|------|--------|
| 1 | Department must be MDR, SA, or WB | Processing Manual |
| 2 | Processor must be an authorised code | Processing Manual |
| 3 | Bin must be GR, BL, AX, or SP | Processing Manual |
| 4 | Category must be alpha / beta / gamma / delta | Processing Manual |
| 5 | Value must be strictly positive | Processing Manual |
| 6 | Timestamp must fall within Q4 2025 | Processing Manual |
| 7 | Nora.K entries after Nov 15 are invalid | Compliance Annex |
| 8 | SP bin restricted to SA department | Compliance Annex |
| 9 | Department–bin authorisation matrix enforced | Compliance Annex |
| 10 | Value must be strictly below 1000.00 | Compliance Annex |
| 11 | Duplicate session IDs: keep earliest by timestamp | Compliance Annex |
| 12 | Sessions must fall on weekdays only | Compliance Annex |
