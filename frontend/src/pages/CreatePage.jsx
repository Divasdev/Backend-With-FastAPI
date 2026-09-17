import { useState } from "react";
import { useNavigate } from "react-router-dom";
export default function CreatePage() {
   const navigate=useNavigate();
   const [form,setForm]=useState({
      title:"",
      language:"",
      code:"",
      description:''
   });

   const [error,setError]=useState(null);
   const [submitting,setSubmitting]=useState(false);

   function handleChange(e){
      setForm({...form,[e.target.name]:e.target.value});
   }

   function handleSubmit(e){
      e.preventDefault();
      setSubmitting(true);
      setError(null);
      fetch('/api/snippets/',{
         method:'POST',
         headers:{
            'content-type':'application/json'},
         body:JSON.stringify(form),
      })
      .then((res)=>{
         if (!res.ok) throw new Error ('Failed to create Snippet');
         return res.json();
      })
      .then(()=>{
         navigate('/');
      })
      .catch((err)=>{
         setError(err.message);
         setSubmitting(false);
      });
   }



  return (
    <section className="editor-page">
      <div className="editor-heading">
        <p className="eyebrow">New snippet</p>
        <h1>Share a Snippet</h1>
        {error& <p style={{color:'red'}}>{error}</p>}

        <p>Paste your code, give it a title, and share it with the community.</p>
      </div>

      <form 
         onSubmit={handleSubmit}
         className="snippet-form"
      >
        <label>
          Title * 
          <input name="title" placeholder="e.g. Debounce utility" required value={form.title} onChange={handleChange} />
        </label>

        <label>
          Language * 
          <input name="language" placeholder="e.g. JavaScript" 
          required value={form.language} onChange={handleChange}/>
        </label>

        <label>
          Code * 
          <textarea
            name="code"
            className="code-input"
            placeholder="Paste your code here…"
            required rows={8}
            value={form.code} onChange={handleChange}
          />
        </label>

        <label>
          Description <span className="optional">(optional)</span>
          <input
            name="description"
            placeholder="A short note about what this snippet does"
            value={form.description} onChange={handleChange}
          />
        </label>

        <div className="form-actions">
          <button type="submit" className="button"
          disabled={submitting}>
            {submitting ? 'Creating...':"Share Snippet "}
            </button>
        </div>
      </form>
    </section>
  );
}