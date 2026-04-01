import { useEffect, useState } from "react";
import styles from "./ListingForm.module.css";

const EMPTY_FORM = {
  type: "misc",
  title: "",
  description: "",
  price_cents: "",
  item_condition: "",
  isbn: "",
  measurements: "",
};

function buildInitialForm(initialData) {
  if (!initialData) return EMPTY_FORM;

  return {
    type: initialData.type || "misc",
    title: initialData.title || "",
    description: initialData.description || "",
    price_cents:
      initialData.price_cents != null
        ? (initialData.price_cents / 100).toFixed(2)
        : "",
    item_condition: initialData.item_condition || "",
    isbn: initialData.isbn || "",
    measurements: initialData.measurements || "",
  };
}

function buildPayload(form) {
  return {
    type: form.type,
    title: form.title.trim(),
    description: form.description.trim() || null,
    price_cents: Math.round(parseFloat(form.price_cents) * 100),
    item_condition: form.item_condition.trim() || null,
    isbn: form.type === "book" && form.isbn.trim() ? form.isbn.trim() : null,
    measurements:
      form.type === "furniture" && form.measurements.trim()
        ? form.measurements.trim()
        : null,
  };
}

export default function ListingForm({
  initialData = null,
  onSubmit,
  onCancel,
  submitText = "Save",
  submittingText = "Saving...",
}) {
  const [form, setForm] = useState(buildInitialForm(initialData));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setForm(buildInitialForm(initialData));
  }, [initialData]);

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      if (!form.title.trim()) {
        throw new Error("Title is required");
      }

      if (!form.price_cents || Number.isNaN(parseFloat(form.price_cents))) {
        throw new Error("Valid price is required");
      }

      const payload = buildPayload(form);
      await onSubmit(payload);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.row}>
        <div className={styles.field}>
          <label className={styles.label}>Category</label>
          <select
            name="type"
            value={form.type}
            onChange={handleChange}
            className={styles.input}
          >
            <option value="misc">Miscellaneous</option>
            <option value="book">Book</option>
            <option value="furniture">Furniture</option>
          </select>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Price ($)</label>
          <input
            name="price_cents"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            value={form.price_cents}
            onChange={handleChange}
            className={styles.input}
            required
          />
        </div>
      </div>

      <div className={styles.field}>
        <label className={styles.label}>Title</label>
        <input
          name="title"
          type="text"
          placeholder="What are you selling?"
          value={form.title}
          onChange={handleChange}
          className={styles.input}
          required
        />
      </div>

      <div className={styles.field}>
        <label className={styles.label}>Description</label>
        <textarea
          name="description"
          placeholder="Describe your item..."
          value={form.description}
          onChange={handleChange}
          className={`${styles.input} ${styles.textarea}`}
          rows={3}
        />
      </div>

      <div className={styles.field}>
        <label className={styles.label}>Condition</label>
        <input
          name="item_condition"
          type="text"
          placeholder="e.g. Like new, Good, Fair"
          value={form.item_condition}
          onChange={handleChange}
          className={styles.input}
        />
      </div>

      {form.type === "book" && (
        <div className={styles.field}>
          <label className={styles.label}>ISBN</label>
          <input
            name="isbn"
            type="text"
            placeholder="978-..."
            value={form.isbn}
            onChange={handleChange}
            className={styles.input}
          />
        </div>
      )}

      {form.type === "furniture" && (
        <div className={styles.field}>
          <label className={styles.label}>Measurements</label>
          <input
            name="measurements"
            type="text"
            placeholder='e.g. 30" W x 20" D x 36" H'
            value={form.measurements}
            onChange={handleChange}
            className={styles.input}
          />
        </div>
      )}

      {error && <p className={styles.formError}>{error}</p>}

      <div className={styles.modalActions}>
        <button
          type="button"
          className={styles.cancelButton}
          onClick={onCancel}
          disabled={submitting}
        >
          Cancel
        </button>
        <button type="submit" className={styles.submitButton} disabled={submitting}>
          {submitting ? submittingText : submitText}
        </button>
      </div>
    </form>
  );
}
