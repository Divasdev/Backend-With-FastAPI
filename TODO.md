# SnipShare: what is left

Tick a box when it is done: change `[ ]` to `[x]`.

## Features

- [x] 1. Author on each snippet. Return the author's email and photo with each snippet and show them on the card.
- [x] 2. Profile page. One page that shows a user and all their snippets.
- [x] 3. Search, filter and sort on the server and feed. Support `?q=`, `?language=` and `?sort=new|top` on `GET /api/snippets/` and provide matching feed controls.
- [x] 4. Pagination. Return 10 snippets by default with a total count, and load additional results with a "Load more" button.
- [x] 5. Votes on the detail page, with the user's current vote and updated score.

## Make it solid

- [x] 6. PostgreSQL. Install Postgres and the driver, change `DATABASE_URL`, fix `check_same_thread` in `database.py` (it is SQLite-only).
- [x] 7. Alembic migrations. Replace `create_all` so table changes are tracked.

## Ship it

- [ ] 9. Deploy. Backend and Postgres on Render or Railway, frontend on Vercel or Netlify. Uploaded photos get wiped on free hosts, decide how to handle that here.
- [ ] 10. README and cleanup. Live link, screenshots, correct setup steps (register is a form, not JSON). Remove `frontend/.vite/deps` from git.

## Bonus, only if I feel like it

- [ ] Docker
- [ ] GitHub Actions to run the tests on every push

## Not doing

Comments, follows, email or password reset, WebSockets, Redis.

## Done so far

Register and login with JWT; profile photo upload; snippet create/read/edit/delete with ownership checks; voting on feed cards and detail pages; author details on snippet cards; user profile pages with their snippets; server-backed feed search, language filtering, newest/top sorting, and pagination; settings from `.env`; React frontend connected.
