import { apiFetch } from './api';

export async function registerAccount({ email, password, profileImage }) {
  // BACKEND INTEGRATION POINT:
  // profileImage is the optional File selected in the registration form.
  // The existing backend accepts JSON, so keep registration working as-is.
  // This file is intentionally NOT uploaded or persisted yet.
  //
  // When you implement multipart registration, replace this request body with:
  const formData  = new FormData();
  
  formData.append('email',email);
  formData.append('password',password);

  if (profileImage){
    formData.append("profile_image",profileImage)
  }


  const response=await fetch('/auth/register',{
    method:'POST',
    body:formData,
  });

const data=await response.json().catch(()=>({}));


if (!response.ok){
  throw new Error (
    data.detail || 'Unable to create account.Please try again.'
  );
}
   return data;

}
