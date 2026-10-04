# Connecting SnipShare: a beginner's debugging guide

This guide explains the bugs found in this project, why the fixes work, and what to learn next. It also reviews your backend as a first independent project. The rating is a subjective code review, not a production certification. The backend was inspected, not fully integration-tested during this change.

## 1. The big picture

Every feature has a chain:

**User action → React handler → HTTP request → FastAPI route → response → React state → screen**

When something breaks, identify the broken step. Avoid changing the whole chain at once.

Swagger successfully calling an endpoint tells you that the backend can handle that request. Your browser might send a different URL, method, body, or headers. Compare the actual requests rather than assuming they are identical.

## 2. What was wrong in this project

### Protected requests did not send the token

Create, update, and delete already used the correct snippet endpoints. They called plain `fetch`, which did not attach the token saved at login. FastAPI requires that token through `get_current_user`, so those requests could be rejected with 401.

Saving a token does not send it anywhere:

```js
localStorage.setItem('token', token);
```

A protected request must include it:

```js
fetch('/api/snippets/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`,
  },
  body: JSON.stringify({
    title: 'Hello',
    language: 'JavaScript',
    code: 'console.log("Hello");',
    description: 'My first snippet',
  }),
});
```

`frontend/src/api/api.js` now centralizes this behavior in `apiFetch`. Pages use that helper instead of repeating token logic.

**Lesson:** authentication must accompany each protected request. Login does not automatically authenticate every later browser request.

### The header did not know login succeeded

The old login handler saved the token and navigated home. The header always rendered the login/register links. It had no user state or condition that could show a different UI.

There are two separate jobs:

| Mechanism | Job |
| --- | --- |
| localStorage | Keep a value across page refreshes |
| React state | Tell React what to render now |

Updating localStorage does not trigger a React render. Updating state does:

```jsx
const [user, setUser] = useState(null);

// After fetching the account:
setUser(profile);

// In the UI:
return user ? <span>Signed in as {user.email}</span> : <Link to="/login">Log in</Link>;
```

`frontend/src/auth/AuthContext.jsx` shares user state between the login page, header, and other pages. `main.jsx` wraps the app in that provider.

**Lesson:** a successful server operation and visible UI feedback are separate responsibilities.

### Refresh lost the in-memory user state

React state starts again when the page reloads. The provider now checks for a saved token and requests `/users/me`. If valid, the profile restores the logged-in UI. While checking, the app shows a loading state. A rejected authenticated request clears the session; a connection failure can be retried.

**Lesson:** persistence needs an explicit restoration step. A saved token alone is not proof that a session is still valid.

### Registration succeeded without explaining the next step

`POST /auth/register` returns the new user's profile, not an access token. Creating an account and logging in are distinct operations in this API. The frontend now confirms account creation and sends the user to login.

**Lesson:** read the response contract. Do not assume registration also signs the user in.

### Requests used inconsistent connection paths

Snippet requests used relative `/api/...` URLs through Vite. Login/register called `http://localhost:8000` directly. That can work with the exact allowed origin, but it introduces CORS and hostname differences. It was a potential browser connection issue, not a proven failure observed in a live browser session.

Now development requests are relative, and Vite forwards `/api`, `/auth`, and `/users` to `http://127.0.0.1:8000`. Restart Vite when changing its configuration.

In production, Vite's development proxy is absent. Configure equivalent reverse-proxy routes or build with `VITE_API_URL` pointing to your backend. For a separate backend origin, configure its CORS allowlist for the frontend origin. Frontend environment variables are public configuration; never place secrets in them.

**Lesson:** a URL beginning with `/` targets the current origin. A development proxy forwards it; React itself does not know where FastAPI runs.

## 3. Your API contract

| Action | Method and path | Request | Success |
| --- | --- | --- | --- |
| Register | POST `/auth/register` | JSON email and password | 201, user profile |
| Login | POST `/auth/login` | URL-encoded username and password | 200, access token |
| Current account | GET `/users/me` | Bearer token | 200, user profile |
| List snippets | GET `/api/snippets/` | Optional offset/limit | 200, array |
| Read snippet | GET `/api/snippets/{id}` | No required token | 200, snippet |
| Create snippet | POST `/api/snippets/` | Bearer token and snippet JSON | 201, snippet |
| Update snippet | PATCH `/api/snippets/{id}` | Owner's token and changed fields | 200, snippet |
| Delete snippet | DELETE `/api/snippets/{id}` | Owner's token | 204, no body |

Login uses `username` for the email because `OAuth2PasswordRequestForm` expects that field name. JSON login credentials would not match this route's contract.

A 204 response has no JSON body to parse. PATCH lets you send just the fields you want to change; the current editor sends all editable fields, which this backend also accepts.

## 4. A debugging routine you can use without AI

1. Open browser DevTools: Console and Network, then filter Network to Fetch/XHR.
2. Perform one action, such as submitting login.
3. If no request appears, check `onSubmit`, `preventDefault`, browser form validation, and Console errors.
4. Inspect the request URL and method. Compare them with the FastAPI route.
5. Inspect the payload and Content-Type. Compare them with the input model or form contract.
6. For protected routes, inspect Request Headers for `Authorization: Bearer ...`. Do not share real tokens in screenshots or logs.
7. Read the response status and response body. The backend's `detail` usually tells you more than a generic frontend message.
8. If the response succeeded, trace the next lines: parsing the response, updating state, displaying feedback, and navigating.
9. Make one targeted change and repeat the same action to verify your explanation.

| Observation | Where to investigate |
| --- | --- |
| 404 | Wrong URL, route prefix, proxy, or missing resource |
| 405 | Wrong HTTP method |
| 422 | Field names, body encoding, or validation rules |
| 401 | Missing/invalid/expired token or wrong login credentials |
| 403 | Signed in but not permitted, such as editing another user's snippet |
| 500 | Backend exception and server logs |
| Network/CORS error | Server availability, browser origin, and proxy/CORS configuration |
| 200/201 but unchanged UI | State update and rendering conditions |

These are clues, not universal diagnoses. Always read the actual response.

## 5. What to learn next, in order

1. **HTTP basics:** URLs, methods, headers, Content-Type, JSON, form encoding, and status codes. Explain each row in the API table in your own words.
2. **JavaScript async behavior:** `async`/`await`, `try`/`catch`/`finally`, and response parsing. Native `fetch` does not throw just because a response is 401 or 500; our helper checks `res.ok` and throws.
3. **React state:** `useState`, conditional rendering, controlled inputs, and loading/error/success states. Build a small fake login UI using state before involving a server.
4. **Shared state:** understand why the header and login page need the same user value. Read the provider and follow where its value is consumed.
5. **Effects and restoration:** learn why session restoration belongs in an effect, what its cleanup does, and why stale requests need care.
6. **Authentication versus authorization:** a token answers who you are; the owner check answers whether you may edit this snippet. Hiding a button is not security—the server must still reject forbidden requests.
7. **Browser networking:** learn origins, CORS, development proxies, and deployment configuration. Reproduce the request manually in DevTools before changing settings.
8. **Testing:** verify success and failure paths, especially missing tokens, invalid input, and cross-account ownership checks.

Do not start by memorizing Context syntax or adding a state-management library. First explain which data each screen needs and what event changes it.

## 6. Small exercises

Do these locally and undo deliberate breakages afterward.

- Replace `apiFetch` with `fetch` for create. Observe the missing bearer header and the backend rejection. Restore the helper.
- Log in, refresh, and watch `/users/me` restore the account UI.
- Register a duplicate email and inspect the response before reading the displayed message.
- Submit a title containing only spaces and inspect the validation response.
- Use two accounts. Create a snippet with account A; verify account B cannot update/delete it, including through a direct API request.
- Stop the backend and submit login. Explain how a connection error differs from incorrect credentials.
- Build a new read-only page that calls an existing endpoint and implements loading, error, empty, and success states yourself.

## 7. Review of your self-written backend

**My rating: 7/10 as a first independently written learning backend.** You have implemented meaningful backend behavior beyond basic CRUD. This score reflects the source code reviewed here, not measured reliability, security testing, or deployment readiness.

### What you did well

- **Password hashing:** you use `PasswordHash.recommended()` and verify hashes instead of storing plaintext passwords.
- **Token authentication:** signed tokens include an expiry and a user ID subject; protected routes resolve the current user through a reusable dependency.
- **Ownership checks:** update and delete compare `owner_id` with the authenticated user. Create derives the owner from the authenticated account rather than trusting a submitted owner ID.
- **Separate schemas:** create, public, update, and user response models separate inputs from outputs. `UserRead` does not expose the password hash.
- **Validation:** required snippet content rejects whitespace-only strings. Partial updates distinguish omitted fields from explicitly invalid null values.
- **Database sessions:** the yielded session dependency scopes cleanup, and parameterized ORM queries avoid manually assembling SQL from user input.
- **Useful API behavior:** bounded pagination, 201 on creation, 404 for missing resources, and 403 for ownership failures.
- **Configuration:** the signing secret comes from settings, and the SQLite database path is anchored to the backend file location.

These are good foundations. The missing frontend authorization header did not mean your protected endpoint was broken; rejecting an unauthenticated write is correct behavior.

### Improvements that would raise the score

1. **Fix malformed token subjects.** In `auth.py`, `int(user_id)` occurs outside the JWT exception handler. A validly signed token with a nonnumeric subject can therefore produce a server exception instead of a clean 401. Validate/convert the subject within guarded code, including relevant type/conversion failures. This does not mean arbitrary attackers can sign valid tokens; it is an input-handling gap.
2. **Strengthen email validation.** `UserCreate.email` is a plain string. Lowercasing helps consistency but does not validate email format or remove accidental surrounding whitespace. Add deliberate validation/normalization and apply the same policy to registration and login.
3. **Handle duplicate-registration races.** Checking for an existing email before inserting is useful, but concurrent requests can both pass that check. Keep the database unique constraint, handle the corresponding integrity error, and roll back before returning a controlled response.
4. **Add backend tests.** No project test suite was found in the inspected files. Start with registration, login, missing/expired tokens, invalid inputs, and account B attempting to edit/delete account A's snippet. These tests protect actual behavior rather than just implementation details.
5. **Make setup reproducible.** The inspected project has no Python dependency manifest. Document or pin the actual dependencies, including settings, JWT, password hashing, and form parsing support, so another person can install and run it reliably.
6. **Improve consistency and readability.** Formatting, type annotations, imports, and whitespace vary across files. Remove unused imports, reduce unnecessary `type: ignore` comments, and keep route functions easy to scan. Readable code makes your next bug easier to find.
7. **Plan schema changes.** `create_all` creates missing tables; it is not a migration strategy for changing existing tables. Learn migrations before you need to preserve deployed user data through schema updates.
8. **Clean up the delete return.** The route declares 204 but returns an object. Make the implementation explicitly return no body so its intent matches the response contract.

For a public deployment, also design login rate limiting, token/session lifecycle, HTTPS configuration, secret management, and appropriate storage of browser credentials. The current localStorage token approach persists conveniently, but JavaScript running on your origin can read it; understand that tradeoff before choosing a production session design.

### What this review does not claim

The backend was not comprehensively tested here. The frontend production build and isolated mocked checks passed for token attachment, anonymous requests, 204 handling, 401 session clearing, and validation errors. A full browser flow against the running backend remains a manual verification step.

## 8. Reading order in this project

1. `backend/App/routers/posts.py`: find the route, method, and authentication requirement.
2. `backend/App/auth.py`: understand login and `get_current_user`.
3. `frontend/src/api/api.js`: see how a request receives its bearer header and how failures become errors.
4. `frontend/src/auth/AuthContext.jsx`: trace login, profile loading, session restoration, and logout.
5. `frontend/src/pages/LoginPage.jsx`: follow submission through success or failure.
6. `frontend/src/components/Layout.jsx`: see shared state become visible account controls.
7. `frontend/src/pages/CreatePage.jsx`: connect a form payload to an authenticated write.

When you can explain this path aloud without looking at the guide, rebuild one small feature yourself. Understanding comes from predicting what the request and screen should do, checking that prediction, and correcting it.
