export default function CreatePage() {
  return (
    <section className="editor-page">
      <div className="editor-heading">
        <p className="eyebrow">New snippet</p>
        <h1>Share a Snippet</h1>
        <p>Paste your code, give it a title, and share it with the community.</p>
      </div>

      <form className="snippet-form">
        <label>
          Title
          <input name="title" placeholder="e.g. Debounce utility" />
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
          <button type="submit" className="button">Share Snippet</button>
        </div>
      </form>
    </section>
  );
}