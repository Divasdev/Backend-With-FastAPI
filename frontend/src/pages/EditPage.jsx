export default function EditPage() {
  return (
    <section className="editor-page">
      <div className="editor-heading">
        <p className="eyebrow">Editing</p>
        <h1>Edit Snippet</h1>
        <p>Update your snippet's details or code below.</p>
      </div>

      <form className="snippet-form">
        <label>
          Title
          <input name="title" placeholder="Snippet title" />
        </label>

        <label>
          Language
          <input name="language" placeholder="e.g. JavaScript" />
        </label>

        <label>
          Code
          <textarea
            name="code"
            className="code-input"
            placeholder="Paste your code here…"
          />
        </label>

        <label>
          Description <span className="optional">(optional)</span>
          <input
            name="description"
            placeholder="A short note about what this snippet does"
          />
        </label>

        <div className="form-actions">
          <button type="submit" className="button">Save Changes</button>
        </div>
      </form>
    </section>
  );
}
