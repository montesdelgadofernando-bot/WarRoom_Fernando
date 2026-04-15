# CareerOS (Local-First SaaS)

CareerOS is a local-first, human-in-the-loop career operations system with a Node.js API and React dashboard.

## Modules

1. **Multi-agent system**: scout, analyst, strategist, recruiter, negotiator.
2. **Revenue engine**: expected value + probability scoring.
3. **CRM**: contacts, interactions, and pipeline tracking.
4. **Execution**: Gmail draft generation (manual review required), plus LinkedIn/Calendar slots in the store.
5. **Dashboard**: KPI cards + EV history chart + opportunity table.
6. **Runtime loop**: backend loop evolves opportunities every 15 seconds.

## Tech Stack

- Backend: Node.js + Express + JSON file storage (`backend/src/data/store.json`)
- Frontend: React + Vite + Tailwind + Recharts
- No external DB (local JSON only)

## Run locally

### 1) Backend

```bash
cd backend
npm install
npm run dev
```

Runs on `http://localhost:4000`.

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`.

## API endpoints

- `GET /health`
- `GET /api/state`
- `POST /api/opportunities`
- `POST /api/crm/contacts`
- `POST /api/execution/drafts`

## Human-in-the-loop rule

All execution artifacts are saved as local drafts with `pending_review` status. CareerOS never auto-sends messages.
