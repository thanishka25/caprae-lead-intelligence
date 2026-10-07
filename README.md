# Caprae Lead Intelligence — Full Stack Developer Pre-Work

A focused lead-generation enhancement inspired by SaaSquatch Leads. The product prioritizes
**lead quality over lead quantity** by combining firmographic filters, deterministic lead scoring,
duplicate detection, and CSV export.

## Why this feature set
SaaSquatch already supports company search, enrichment, filtering, saving/exporting leads and
company insights. This challenge implementation focuses on the next step: turning a list of
possible leads into an **actionable ranked queue** for outreach.

### Core workflow
1. Filter companies by industry, location, size and revenue.
2. Rank leads using an explainable score.
3. Review the signals behind each score.
4. Remove duplicates.
5. Export the prioritized list to CSV.

The score is intentionally deterministic and explainable rather than pretending to be an opaque
AI prediction. This makes it easier for a sales/search-fund team to trust and audit.

## Stack
- Frontend: React + Vite
- Backend: FastAPI + Pydantic
- Database: SQLite (replaceable with PostgreSQL for production)
- Data access: SQLAlchemy
- API: REST
- Containerization: Docker + Docker Compose
- Deployment recommendation: static frontend on Vercel/CloudFront and FastAPI API on AWS ECS/Fargate
  or an Ubuntu VM; PostgreSQL + Redis can be introduced when traffic requires them.

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## API
- `GET /api/health`
- `GET /api/leads`
- `GET /api/leads/{id}`
- `GET /api/stats`
- `GET /api/export.csv`

Query parameters for `/api/leads`:
`industry`, `location`, `min_employees`, `max_employees`, `min_revenue`,
`min_score`, `sort`, `limit`.

## Performance / architecture notes
- Server-side filtering avoids shipping an unnecessary dataset to the browser.
- SQLite indexes support common filter/sort fields.
- Score calculation is O(n) over the filtered result set.
- The frontend uses a debounced filter request.
- Production caching can use Redis for repeated ICP queries and expensive enrichment calls.
- External enrichment should run asynchronously through a job queue so the UI never waits on
  third-party providers.
- Deduplication uses normalized domain as the primary company key and a normalized name/domain
  fallback.

## Ethical data handling
The demo dataset is synthetic. A production version should only collect permitted public/business
data, respect provider terms and robots/rate limits where applicable, minimize personal data,
provide provenance for enriched fields, and avoid sensitive demographic targeting.

## Time-box
The implementation is intentionally scoped to the handbook's five-hour constraint. It prioritizes
one high-impact workflow instead of trying to recreate the entire SaaSquatch platform.