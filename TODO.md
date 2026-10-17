# SnipShare: what is left

Tick a box when it is done: change `[ ]` to `[x]`.

## Features

- [x] 1. Author on each snippet. The API only returns `owner_id`, so return the author's email and photo with each snippet and show them on the card.
- [x] 2. Profile page. One page that shows a user and all their snippets.
- [ ] 3. Search, filter and sort on the server. Add `?q=`, `?language=` and `?sort=new|top` to `GET /api/snippets/`.
- [ ] 4. Pagination. Lower the default `limit` from 100 to about 10, return the total count, add a "Load more" button.
- [ ] 5. Votes on the detail page. They only show on the feed right now.

## Make it solid

- [ ] 6. Tests with pytest. About 10 to 15: register, login, create needs a token, can't edit someone else's snippet, voting twice doesn't double count.
- [ ] 7. PostgreSQL. Install Postgres and the driver, change `DATABASE_URL`, fix `check_same_thread` in `database.py` (it is SQLite-only).
- [ ] 8. Alembic migrations. Replace `create_all` so table changes are tracked.

## Ship it

- [ ] 9. Deploy. Backend and Postgres on Render or Railway, frontend on Vercel or Netlify. Uploaded photos get wiped on free hosts, decide how to handle that here.
- [ ] 10. README and cleanup. Live link, screenshots, correct setup steps (register is a form, not JSON). Remove `frontend/.vite/deps` from git.

## Bonus, only if I feel like it

- [ ] Docker
- [ ] GitHub Actions to run the tests on every push

## Not doing

Comments, follows, email or password reset, WebSockets, Redis.

## Done so far

Register and login with JWT, profile photo upload, snippet create/read/edit/delete with ownership checks, voting, settings from `.env`, React frontend connected.
