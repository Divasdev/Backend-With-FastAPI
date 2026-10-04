import { apiFetch } from './api';

export async function registerAccount({ email, password, profileImage }) {
  // BACKEND INTEGRATION POINT:
  // profileImage is the optional File selected in the registration form.
  // The existing backend accepts JSON, so keep registration working as-is.
  // This file is intentionally NOT uploaded or persisted yet.
  //
  // When you implement multipart registration, replace this request body with:
  // const body = new FormData();
  // body.append('email', email.trim());
  // body.append('password', password);
  // if (profileImage) body.append('profile_image', profileImage);
  // Pass `body` to apiFetch and REMOVE the Content-Type header: the browser
  // supplies multipart/form-data with the required boundary automatically.
  //
  // Have GET /users/me return `profile_image_url` (absolute/public URL or null).
  // AuthProvider already loads that response at login and on refresh; Layout
  // reads this field to show the saved photo. Never store a blob preview URL
  // as the account image: it exists only in this browser page's lifetime.
  void profileImage;
  return apiFetch('/auth/register', {
    anonymous: true,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.trim(), password }),
  });
}
