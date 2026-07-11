# AI Architect — Run Guide

This covers everything needed to run the complete project: backend (10 phases)
and frontend (12 phases).

## 1. Backend

```bash
cd "AI Architect/backend"
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at **http://127.0.0.1:8000**. Check it's alive:
- http://127.0.0.1:8000/docs — interactive Swagger UI for every endpoint

### Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/generate` | Floor plan + rooms + cost + materials + Vastu (JSON) |
| POST | `/generate-report` | Same, as a downloadable PDF |
| POST | `/material-estimate` | Material quantities for an area |
| POST | `/budget-optimizer` | What fits a given budget |
| POST | `/wall-design` | Wall design suggestions by room type |
| POST | `/chat` | Rule-based chatbot (natural language) |
| POST | `/save-plan` | Manually save a plan to history |
| GET | `/history/{user_id}` | List a user's saved plans |
| GET | `/history/{user_id}/{plan_id}` | One saved plan's full detail |
| DELETE | `/history/{user_id}/{plan_id}` | Delete a saved plan |

History is stored in `backend/ai_architect.db` (SQLite, auto-created on first run).

## 2. Frontend

In a **second terminal**, with the backend still running:

```bash
cd "AI Architect/frontend"
npm install
npm run dev
```

Frontend runs at **http://localhost:5173** (Vite will print the exact URL).

By default the frontend calls the backend at `http://127.0.0.1:8000`. To point
it elsewhere (e.g. a deployed backend), copy `.env.example` to `.env` and set:
```
VITE_API_URL=https://your-backend-url
```

## 3. First-time checklist

1. Backend running, `/docs` loads in browser → backend OK
2. Frontend running, login screen appears at `localhost:5173` → enter any name
3. Go to **Floor plan** tab → fill in area/BHK/bathrooms → Generate → image + tables should appear
4. Go to **AI chat** tab → try a suggestion chip → should get a reply
5. Go to **Dashboard** tab → should show your saved plan count

If step 3 fails with a network error, the most common cause is the backend
not running, or a typo'd `VITE_API_URL`.

## 4. Known gaps / honest notes

- **Login (Phase 12)** is local-only (browser storage), not real authentication
  with passwords — it just keeps plans organized per name. For real accounts,
  a proper auth backend (sessions or JWT + a users table) would be needed.
- **3D preview (Phase 7)** is a CSS-based illustrative block view, not a true
  3D engine — added this way to avoid extra heavy dependencies (e.g. Three.js).
- **Voice assistant (Phase 10)** relies on the browser's Web Speech API, which
  is well-supported in Chrome/Edge but not in Firefox or Safari.
- This codebase was developed without live `npm install` / `uvicorn` access in
  the dev sandbox (no network there). Every backend logic module was tested
  directly with real inputs; the frontend was checked for syntax correctness
  and import/export consistency, but not run live. Please run the checklist
  above and report back anything that breaks.
