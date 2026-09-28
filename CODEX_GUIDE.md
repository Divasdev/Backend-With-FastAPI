# SnipShare — Codex Project Guide

A 10-minute project walkthrough, an honest review of the completed CRUD milestone, and a learning path for authentication and authorization.

**Review date:** September 28, 2026. This guide describes the code at the time of review. Authentication examples below are proposed next steps, not existing features.

During the review, **35 backend checks passed against an isolated, in-memory SQLite database**, and the **React production build passed**. These checks covered CRUD, validation, pagination, partial updates, and missing records. They were temporary verification, not a committed test suite. Browser interactions were not tested.

## 1. Start at the actual entry point

Your backend entry point is [`backend/App/main.py`](backend/App/main.py).

Start the backend from the project root:

```bash
cd backend
python3 -m uvicorn App.main:app --reload --host 127.0.0.1 --port 8000
```

That command tells Uvicorn to:

- Import the `App.main` Python module.
- Find the object named `app`.
- Serve that application over HTTP.
- Restart during development when the source changes.

**Uvicorn is the server handling incoming connections. FastAPI is the application that decides which function handles each request.**

Inside the entry point:

```python
app = FastAPI()
```

You create the application, configure CORS, register a startup function, and attach the snippets router:

```python
app.include_router(posts.router)
```

That separation is useful: `main.py` assembles the application, while the router contains its snippet-related behavior.

The startup function calls `create_db_and_tables()`, which creates any missing database tables. Importing the posts router also imports your models, so SQLModel knows about the `Snip` table by the time startup runs.

**The repository's root `main.py` is a separate Heroes practice exercise. It is not SnipShare's entry point.**

An interview explanation:

> “SnipShare is a code-sharing application with a React frontend and a FastAPI backend. The backend entry point configures the application and registers a router that exposes snippet CRUD operations.”

## 2. Follow a request through the system

```text
React page
    ↓ HTTP request to /api/...
Vite development proxy
    ↓ forwards to the backend
FastAPI router
    ↓ request validation + database dependency
SQLModel session
    ↓ database operations
SQLite
    ↓ result
FastAPI response model → JSON response → React updates the screen
```

The Vite proxy is part of your **development setup**. In [`frontend/vite.config.js`](frontend/vite.config.js), requests beginning with `/api` are forwarded to the backend on port 8000.

That allows React to write:

```javascript
fetch('/api/snippets/')
```

The frontend does not need to repeat the backend hostname in every component. A production deployment will need its own routing configuration for these API requests.

Your CORS configuration permits `http://localhost:5173` when making cross-origin browser requests. With the development proxy, the browser normally sees a same-origin request to Vite.

**CORS does not identify users or protect snippet ownership.** Setting `allow_credentials=True` does not implement authentication.

## 3. Understand the frontend entry chain

```text
frontend/index.html
    → frontend/src/main.jsx
    → App.jsx
    → Layout
    → selected page
```

[`main.jsx`](frontend/src/main.jsx) mounts React into the `root` element and wraps the application in `BrowserRouter`.

[`App.jsx`](frontend/src/App.jsx) maps URLs to pages:

| Browser URL | Page behavior |
|---|---|
| `/` | Fetch and display snippets |
| `/posts/:id` | Display one snippet and its edit/delete actions |
| `/create` | Submit a new snippet |
| `/posts/:id/edit` | Load a snippet and submit changes |
| `/login`, `/register` | Display authentication placeholders |

[`Layout.jsx`](frontend/src/components/Layout.jsx) provides the shared navigation and footer. Its `<Outlet />` is where the selected page appears.

Notice the distinction:

- `/posts/5` is a **frontend page URL**.
- `/api/snippets/5` is a **backend API URL**.

React Router chooses the screen; FastAPI chooses the server-side operation.

## 4. Trace “Create Snippet” from the form to the database

In [`CreatePage.jsx`](frontend/src/pages/CreatePage.jsx), submitting the form:

1. Prevents the browser's default form submission.
2. Sets `submitting` to `true`.
3. Sends the form as JSON to `POST /api/snippets/`.
4. Checks whether the response succeeded.
5. Navigates back to the feed on success.

The disabled submit button and visible error state are worthwhile details. They make the interface behave sensibly while the request is running.

On the backend, this request reaches [`posts.py`](backend/App/routers/posts.py):

```python
@router.post("/", response_model=SnipPublic)
def create_snip(snip: SnipCreate, session: SessionDep):
    db_snip = Snip.model_validate(snip)
    session.add(db_snip)
    session.commit()
    session.refresh(db_snip)
    return db_snip
```

There is a lot happening in this short function:

- `snip: SnipCreate` tells FastAPI what the request body must look like. FastAPI uses the model to parse and validate JSON before executing the route function.
- `session: SessionDep` asks FastAPI to provide a database session.
- `response_model=SnipPublic` defines the response contract: which fields the API returns and their expected types.
- `Snip.model_validate(snip)` creates the database-model instance from the validated input.

An interview explanation:

> “My endpoint declares its request schema, database dependency, and response schema. FastAPI uses those declarations for validation, dependency injection, serialization, and API documentation.”

You can explore that generated documentation at `http://127.0.0.1:8000/docs` while the backend is running.

## 5. Understand the model separation

Your model separation is one of the strongest parts of the implementation.

In [`models.py`](backend/App/models.py), five models have distinct jobs:

| Model | Responsibility |
|---|---|
| `SnipBase` | Shared snippet fields and validation |
| `Snip` | Database table, including generated/default fields |
| `SnipCreate` | Fields accepted when creating a snippet |
| `SnipPublic` | Fields returned to API clients |
| `SnipUpdate` | Fields accepted for partial updates |

Only `Snip` has `table=True`. The others define data shapes without creating additional tables.

Clients can supply `title`, `language`, `code`, and `description`, while the server controls `id`, `created_at`, and `vote_count`.

The review checks confirmed that sending a custom `id` or `vote_count` during creation does not override those values. Currently, these extra input fields are **ignored rather than rejected**.

Your validation rejects whitespace-only titles, languages, and code:

```python
if not value.strip():
    raise ValueError("Must not be blank")
return value
```

The return statement matters. You use `.strip()` to check whether content exists, but return the original value. **That preserves indentation in submitted code**, which is exactly what a snippet application needs.

Your `created_at` field uses `default_factory=date.today`, so the default is calculated when an object is created. It currently records a calendar date, not a full timestamp.

## 6. Understand the engine, session, and dependency injection

In [`database.py`](backend/App/database.py), the SQLite path is built relative to the Python file:

```python
sqlite_file_path = Path(__file__).resolve().parent / "database.db"
```

That avoids accidentally selecting a different database just because you launched the server from another directory. The active database is `backend/App/database.db`.

You create an engine and define:

```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

Think of the **engine** as the shared database connection infrastructure. A **session** tracks the database work performed for a request.

When a route asks for `SessionDep`, FastAPI runs the dependency and supplies the yielded session. The context manager closes it when the dependency finishes.

Your routes do not repeat session setup and cleanup. This means less duplicated code and a clear place to substitute database access during testing.

The SQLite setting `check_same_thread=False` permits connection use across threads. It does not make a session safe to share across concurrent requests; your per-request session pattern remains important.

Back in the create operation:

```python
session.add(db_snip)
session.commit()
session.refresh(db_snip)
```

These have different purposes:

| Call | Purpose |
|---|---|
| `add()` | Places the object under the session's management, pending persistence |
| `commit()` | Flushes pending changes and commits the transaction |
| `refresh()` | Reloads the object from the database, including its generated ID |

Be comfortable explaining those three lines individually.

Your regular `def` endpoints fit your synchronous database operations. FastAPI runs synchronous route functions in a thread pool. Merely changing them to `async def` would not make synchronous database calls nonblocking. See [FastAPI's concurrency documentation](https://fastapi.tiangolo.com/async/#path-operation-functions).

## 7. Walk through the rest of CRUD

Your router exposes:

| Method and path | Operation |
|---|---|
| `POST /api/snippets/` | Create |
| `GET /api/snippets/` | List |
| `GET /api/snippets/{id}` | Read one |
| `PATCH /api/snippets/{id}` | Partially update |
| `DELETE /api/snippets/{id}` | Delete |

### Listing and reading

The list operation orders by descending ID and supports pagination:

```python
select(Snip).order_by(Snip.id.desc()).offset(offset).limit(limit)
```

You validate that `offset >= 0` and `1 <= limit <= 100`. This prevents invalid pagination values and bounds the number of returned rows.

Reading one record uses:

```python
session.get(Snip, id)
```

If no matching record exists, you raise `HTTPException(status_code=404, ...)`. Updating and deleting also check existence first.

The frontend feed fetches real API data; [`demoPosts.js`](frontend/src/data/demoPosts.js) is no longer driving it. Language filtering happens locally in React. Consequently, it filters only the fetched records—currently the first 100 by default—not every snippet that might exist in the database.

### Partial updates: a strong interview topic

Your update route uses:

```python
snip_data = snip.model_dump(exclude_unset=True)
snip_db.sqlmodel_update(snip_data)
```

Suppose the existing snippet has a title, language, code, and description. A client sends:

```json
{
  "title": "A better title"
}
```

`exclude_unset=True` produces a dictionary containing only `title`. The other fields remain unchanged.

Without that distinction, optional fields could accidentally overwrite existing data with their defaults.

You deliberately handle three different cases:

| PATCH body | Meaning in your API |
|---|---|
| `{}` | Leave everything unchanged |
| `{"description": ""}` | Clear the description |
| `{"description": null}` | Reject the request |

**An omitted field and an explicitly supplied null are different inputs**, and your validators preserve that distinction.

The React edit form currently submits all four editable fields, but the backend supports smaller partial updates too. The review verified that a title-only update preserves the remaining data.

### Deleting and responding

Deletion loads the snippet, returns `404` if it does not exist, otherwise calls `session.delete()` and `session.commit()`. The API returns `{"ok": true}` on success.

Remember these current status codes:

- `422`: the request fails validation.
- `404`: the requested record does not exist.
- `200`: successful operations, including creation.

Returning `201 Created` for the POST endpoint would be a useful small improvement.

## 8. What you have done well

The strongest decisions are the ones you can explain through their consequences:

| Decision | Why it helps |
|---|---|
| Separate input, output, and table models | Controls what clients can submit and receive |
| Reusable session dependency | Keeps database session setup and cleanup consistent |
| `exclude_unset=True` for PATCH | Preserves data the client did not ask to change |
| Explicit null and blank validation | Gives the API predictable update semantics |
| Server-side validation | Enforces rules even when someone bypasses the React form |
| Validation that preserves original code | Keeps meaningful indentation and whitespace |
| Pagination bounds and explicit ordering | Bounds list size and gives a predictable order |
| File-relative database path | Avoids working-directory-dependent database selection |
| Loading, submission, and error states | Makes the frontend handle the request lifecycle |
| Separate app setup and router | Gives future features a clear place to live |

You also check `res.ok` in the frontend. This matters because `fetch()` can resolve successfully at the network level while the server returns an HTTP error.

These are concrete strengths to discuss in an interview. You can point to working behavior behind each one.

## 9. Development gaps to acknowledge honestly

These are sensible next steps for an application still being developed:

1. **Authentication and ownership are unimplemented.** Anyone who can reach the API can currently create, edit, or delete snippets. The login/register forms do not contact the server. The `owner_id` values in demo data do not implement ownership in the real backend.

2. **There is no committed test suite or Python dependency manifest.** Saving meaningful API tests and declaring backend dependencies would make the project easier to reproduce. The temporary review checks are evidence of current behavior, not ongoing regression protection.

3. **Database migrations are the next database concept to learn.** `create_all()` creates missing tables; it does not migrate existing tables when your models change. This will matter when adding users and ownership.

4. **Frontend errors lose useful detail.** The API can report which field failed validation, but the forms show generic messages such as “Failed to create Snippet.”

5. **The feed has no pagination controls yet.** The backend supports pagination, but React currently fetches one page. Server-side language filtering would also be useful as the dataset grows.

6. **Some repository cleanup would help.** Both SQLite database files are tracked. The separate root Heroes exercise fails to import because `HeroUpdate` is not a valid Pydantic/SQLModel request model; it also contains a placeholder `model_dump()` that raises `NotImplementedError`. Keep that exercise clearly separate from the working application.

7. **The startup hook uses an older API.** It works in the reviewed environment, but FastAPI now recommends `lifespan` instead of `@app.on_event("startup")`. See [FastAPI lifespan documentation](https://fastapi.tiangolo.com/advanced/events/).

8. **Voting is display-only.** A `vote_count` field and vote symbols are present, but there is no voting API or interactive voting behavior yet.

## 10. Learn authentication and authorization next

**Authentication establishes who is making a request. Authorization decides whether that person may perform the requested action.**

For SnipShare, a useful initial policy would be:

| Action | Proposed permission |
|---|---|
| Browse/read snippets | Anyone |
| Create a snippet | Logged-in user |
| Edit/delete a snippet | Its owner |

This is a proposed design. It is not enforced by the current code.

### Step 1: Add users and registration

Create a database `User` model, a registration input model, and a public output model. Your existing snippet schema separation provides the pattern.

Enforce unique usernames/emails in the database. Store a password hash and keep it out of public responses. FastAPI's current security tutorial uses `pwdlib` with Argon2 for password hashing. See the [official security tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).

### Step 2: Add login and credential verification

Find the user and verify the submitted password against the stored hash.

For a JWT learning implementation, issue a short-lived signed token containing a user identifier in `sub` and an expiration in `exp`. JWT contents are readable; do not put passwords or secrets inside them. See [FastAPI JWT guidance](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#about-jwt).

### Step 3: Build a reusable current-user dependency

Your existing dependency-injection knowledge applies directly:

```python
# Proposed pattern; not implemented in the current project.
CurrentUser = Annotated[User, Depends(get_current_user)]
```

`get_current_user` should validate the token's signature and expiry, extract the user identifier, and load the user. `OAuth2PasswordBearer` extracts the bearer token; your verification code still needs to establish whether it is valid. See the [FastAPI security implementation](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).

A protected route will then declare both the database session and the current user as dependencies.

### Step 4: Add snippet ownership and enforce it in the backend

Add an `owner_id` foreign key to `Snip`. When creating a snippet, assign ownership from `current_user.id`. The client should not choose the owner.

Before an update or deletion, check ownership after loading the snippet:

```python
# Proposed authorization check; not implemented yet.
if snippet.owner_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not permitted")
```

For this policy:

- Missing or invalid authentication should produce `401`.
- An authenticated user attempting a forbidden action should receive `403`.
- A nonexistent snippet should still produce `404`.

Plan how existing snippets will acquire owners when you migrate the database. Adding a required owner column involves both a schema change and a decision about existing data.

### Step 5: Connect the React authentication pages

Wire registration and login to the API, maintain current-user state, and show edit/delete controls for the owner.

Frontend checks improve the interface; backend checks enforce permission. Someone can send an HTTP request directly without using your buttons.

Learn token storage and cookie/session tradeoffs before deciding how login persists across reloads. Also ensure the login form sends the format your endpoint expects; an endpoint using `OAuth2PasswordRequestForm` expects form data rather than the JSON used by your snippet forms.

### Step 6: Test with two users

Use this scenario as your acceptance test:

1. Alice creates a snippet.
2. Bob can read it.
3. Bob cannot edit or delete it.
4. Alice can edit and delete it.
5. An unauthenticated request cannot create a snippet.
6. An expired token fails authentication.
7. User responses never expose password hashes.
8. A client cannot assign a newly created snippet to another user.

The two-user scenario is the clearest proof that you implemented authorization as well as login.

Refresh tokens, logout/revocation, password resets, and admin roles can follow after that foundation works.

## 11. Practice your interview explanation

Say this in your own words:

> “I'm building SnipShare to learn FastAPI through a complete application. I've implemented snippet CRUD with React, FastAPI, SQLModel, and SQLite. I separated database models from request and response schemas, used dependency injection for database sessions, and added validation, bounded pagination, and partial updates that preserve omitted fields. My next milestone is user authentication and ownership-based authorization, so users can edit and delete only their own snippets.”

Before the interview, make sure you can explain:

- Why `backend/App/main.py` is the actual entry point.
- What Uvicorn does compared with FastAPI.
- Why `SnipCreate`, `SnipPublic`, and `Snip` are separate.
- What `Depends()` and `yield` accomplish in the session dependency.
- How `add()`, `commit()`, and `refresh()` differ.
- Why PATCH uses `exclude_unset=True`.
- How an omitted field differs from an explicit `null`.
- Why synchronous `def` routes fit the current database setup.
- Why CORS and hidden frontend buttons do not enforce ownership.
- How authentication and authorization will build on the current design.
