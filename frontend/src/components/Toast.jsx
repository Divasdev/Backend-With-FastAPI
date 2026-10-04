import { useEffect, useState } from 'react';

// Mounted in Layout so feedback stays visible after a page navigation.
export default function Toast({ message, onDismiss }) {
  const [hovered, setHovered] = useState(false);
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    if (!message || hovered || focused) return;
    const timer = window.setTimeout(onDismiss, 8000);
    return () => window.clearTimeout(timer);
  }, [message, onDismiss, hovered, focused]);

  return (
    <div className="toast-region" aria-live="polite" aria-atomic="true">
      {message && <div className="toast" onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
        onFocus={() => setFocused(true)} onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setFocused(false); }}>
        <span className="toast-icon" aria-hidden="true">✓</span>
        <p>{message}</p>
        <button type="button" onClick={onDismiss} aria-label="Dismiss notification">×</button>
      </div>}
    </div>
  );
}
