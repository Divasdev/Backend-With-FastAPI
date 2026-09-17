import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

export default function EditPage() {
   const { id } = useParams();
   const navigate = useNavigate();

   const [form, setForm] = useState(null);
   const [loading, setLoading] = useState(true);
   const [error, setError] = useState(null);
   const [submitting, setSubmitting] = useState(false);

   useEffect(() => {
      fetch(`/api/snippets/${id}`)
         .then((res) => {
            if (!res.ok) {
               throw new Error("Cou   ld not load snippet");
            }

            return res.json();
         })
         .then((data) => {
            setForm({
               title: data.title,
               language: data.language,
               code: data.code,
               description: data.description || "",
            });

            setLoading(false);
         })
         .catch((err) => {
            setError(err.message);
            setLoading(false);
         });
   }, [id]);

   function handleChange(e) {
      setForm({
         ...form,
         [e.target.name]: e.target.value,
      });
   }

   function handleSubmit(e) {
      e.preventDefault();

      setSubmitting(true);
      setError(null);

      fetch(`/api/snippets/${id}`, {
         method: "PATCH",
         headers: {
            "Content-Type": "application/json",
         },
         body: JSON.stringify(form),
      })
         .then((res) => {
            if (!res.ok) {
               throw new Error("Failed to update");
            }

            return res.json();
         })
         .then(() => {
            navigate(`/posts/${id}`);
         })
         .catch((err) => {
            setError(err.message);
            setSubmitting(false);
         });
   }

   if (loading) {
      return <p>Loading...</p>;
   }

   if (error) {
      return <p>{error}</p>;
   }

   return (
      <section className="editor-page">
         <div className="editor-heading">
            <p className="eyebrow">Editing</p>

            <h1>Edit Snippet</h1>

            <p>Update your snippet&apos;s details or code below.</p>
         </div>

         <form className="snippet-form" onSubmit={handleSubmit}>
            <label>
               Title

               <input
                  name="title"
                  placeholder="Snippet title"
                  required
                  value={form.title}
                  onChange={handleChange}
               />
            </label>

            <label>
               Language

               <input
                  name="language"
                  placeholder="e.g. JavaScript"
                  required
                  value={form.language}
                  onChange={handleChange}
               />
            </label>

            <label>
               Code

               <textarea
                  name="code"
                  className="code-input"
                  placeholder="Paste your code here…"
                  required
                  rows={8}
                  value={form.code}
                  onChange={handleChange}
               />
            </label>

            <label>
               Description{" "}
               <span className="optional">(optional)</span>

               <input
                  name="description"
                  placeholder="A short note about what this snippet does"
                  value={form.description}
                  onChange={handleChange}
               />
            </label>

            <div className="form-actions">
               <button
                  type="submit"
                  className="button"
                  disabled={submitting}
               >
                  {submitting ? "Saving..." : "Save Changes"}
               </button>
            </div>
         </form>
      </section>
   );
}