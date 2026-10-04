import { useState } from 'react';

// Expected account field: profile_image_url, an absolute/public image URL or null.
// The current backend can omit it; the initials remain visible instead.
export default function Avatar({ src, email = '', large = false }) {
  const [failedSrc, setFailedSrc] = useState(null);
  const initials = email.trim().slice(0, 2).toUpperCase() || '?';

  return (
    <span className={`avatar${large ? ' avatar-large' : ''}`}>
      {src && failedSrc !== src ? (
        <img src={src} alt="Profile photo" onError={() => setFailedSrc(src)} />
      ) : (
        <span role="img" aria-label="Default profile avatar">{initials}</span>
      )}
    </span>
  );
}
