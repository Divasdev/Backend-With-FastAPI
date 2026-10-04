import { useEffect, useRef, useState } from 'react';
import Avatar from './Avatar';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_BYTES = 5 * 1024 * 1024;

export default function ProfileImagePicker({ file, onChange, email, disabled }) {
  const inputRef = useRef(null);
  const [preview, setPreview] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!file) {
      setPreview('');
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    // Release the temporary browser URL after replacement, removal or navigation.
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function handleChange(event) {
    const selected = event.target.files?.[0];
    if (!selected) return;
    if (!ACCEPTED_TYPES.includes(selected.type) || selected.size > MAX_BYTES) {
      setError('Choose a JPG, PNG or WebP image no larger than 5 MB.');
      event.target.value = '';
      return;
    }
    setError('');
    onChange(selected);
  }

  function removeImage() {
    onChange(null);
    setError('');
    inputRef.current.value = '';
  }

  return (
    <div className="profile-image-picker">
      <div className="profile-image-heading">
        <Avatar key={preview} src={preview} email={email} large />
        <div>
          <label htmlFor="profile-image">Profile photo <span className="optional">(optional)</span></label>
          <p id="profile-image-help">JPG, PNG or WebP · up to 5 MB</p>
        </div>
      </div>
      <input
        ref={inputRef}
        id="profile-image"
        name="profile_image"
        type="file"
        accept={ACCEPTED_TYPES.join(',')}
        disabled={disabled}
        onChange={handleChange}
        aria-describedby={`profile-image-help profile-image-preview-note${error ? ' profile-image-error' : ''}`}
        aria-invalid={Boolean(error)}
      />
      {file && <div className="profile-image-selection">
        <span>{file.name}</span>
        <button type="button" className="text-button" disabled={disabled} onClick={removeImage}>Remove photo</button>
      </div>}
      <p id="profile-image-preview-note" className="profile-image-note">Preview only for now. Your photo won’t be saved with your account yet.</p>
      {error && <p id="profile-image-error" className="notice error" role="alert">{error}</p>}
    </div>
  );
}
