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
for the API documentation. The Vite development server forwards `/api`, `/auth`, and `/users` requests
to the backend. Both servers must stay running. Stop each with Ctrl+C.

The backend uses `backend/App/database.db`, independent of the directory from
which it is started. The root `main.py` is a separate Heroes practice exercise;
it is not the SnipShare entry point.

If dependencies are missing, install `fastapi`, `sqlmodel`, and `uvicorn` in your
Python environment and run `npm install` in `frontend`.

## How the frontend connects

All requests use `frontend/src/api/api.js`. In development, URLs are relative;
Vite proxies them to FastAPI on port 8000. Restart Vite after changing its config.
For deployment, either configure the web server to proxy these same paths or set
`VITE_API_URL` to the backend origin when building the frontend. A separate origin
must be included in the backend CORS allowlist. Vite's proxy only runs in development.

- Register: `POST /auth/register` with JSON `{ email, password }`. Creates the account, then displays a confirmation on the login page; it does not return a token.
- Login: `POST /auth/login` with URL-encoded `username` (the email) and `password`. Saves `access_token`, then fetches `GET /users/me` to display the account.
- List/detail: `GET /api/snippets/` and `GET /api/snippets/{id}`.
- Create: `POST /api/snippets/` with JSON `{ title, language, code, description }`.
- Update: `PATCH /api/snippets/{id}` with the fields to change as JSON.
- Delete: `DELETE /api/snippets/{id}`; success has no response body.

`apiFetch` automatically attaches `Authorization: Bearer <token>` and surfaces
backend errors, including validation messages. `AuthProvider` holds reactive user
state; writing localStorage alone cannot update React's UI. Create/edit routes
require login. Edit/delete buttons appear only for the owner, and the backend
still enforces ownership. A 401 from an authenticated request clears the session.

## Quick manual check

1. Register a new account: check the confirmation on the login page.
2. Log in: check your email and the Log out button in the header.
3. Refresh: your signed-in state should return after the session check.
4. Share a snippet, edit it, then delete it.
5. Log out: account controls disappear; opening `/create` sends you to login.
6. Try an incorrect password or duplicate email: an error should be visible.
