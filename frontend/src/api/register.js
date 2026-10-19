import { API_URL } from './api';

export async function registerAccount({ email, password, profileImage }) {
  const formData = new FormData();

  formData.append('email', email);
  formData.append('password', password);

  if (profileImage) {
    formData.append('profile_image', profileImage);
  }

  let response;
  try {
    response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      body: formData,
    });
  } catch {
    throw new Error('Could not reach the server. Check that the backend is running.');
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => `${item.loc?.at(-1) || 'Field'}: ${item.msg}`).join('; ')
      : data.detail;
    throw new Error(typeof detail === 'string' ? detail : 'Unable to create account. Please try again.');
  }

  return data;
}
