import { useState } from 'react';
import { API_URL } from '../api/api';

// Expected account field: profile_image_url, an absolute/public image URL or null.
// The current backend can omit it; the initials remain visible instead.
export default function Avatar({ src, email = '', large = false, small = false }) {
  const [failedSrc, setFailedSrc] = useState(null);
  const initials = email.trim().slice(0, 2).toUpperCase() || '?';
  const resolvedSrc = src && !src.startsWith('http') && !src.startsWith('data:') && API_URL ? `${API_URL}${src}` : src;

  return (
    <span className={`avatar${large ? ' avatar-large' : ''}${small ? ' avatar-small' : ''}`}>
      {resolvedSrc && failedSrc !== resolvedSrc ? (
        <img src={resolvedSrc} alt="Profile photo" onError={() => setFailedSrc(resolvedSrc)} />
      ) : (
        <span role="img" aria-label="Default profile avatar">{initials}</span>
      )}
    </span>
  );
}
