# SnipShare

React frontend with a synchronous FastAPI and SQLModel backend.

## Run locally

From the project directory, open two terminals.

Backend:

```sh
cd backend
python3 -m uvicorn App.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```sh
cd frontend
npm run dev -- --host localhost --port 5173 --strictPort
```

Open http://localhost:5173 for the app and http://127.0.0.1:8000/docs
for the API documentation. The Vite development server forwards `/api` requests
to the backend. Both servers must stay running. Stop each with Ctrl+C.

The backend uses `backend/App/database.db`, independent of the directory from
which it is started. The root `main.py` is a separate Heroes practice exercise;
it is not the SnipShare entry point.

If dependencies are missing, install `fastapi`, `sqlmodel`, and `uvicorn` in your
Python environment and run `npm install` in `frontend`.

Registration and login are still placeholders. Snippet CRUD currently has no
authentication or ownership checks; this is a local learning app.
