import { useEffect, useState } from "react";
import ItemCard from "../../components/itemcard/ItemCard.jsx";
import styles from "./Market.module.css";

const EMPTY_FORM = {
  type: "misc",
  title: "",
  description: "",
  price_cents: "",
  item_condition: "",
  isbn: "",
  measurements: "",
};

function CreateListingModal({ onClose, onCreated }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const payload = {
      type: form.type,
      title: form.title.trim(),
      description: form.description.trim() || null,
      price_cents: Math.round(parseFloat(form.price_cents) * 100),
      item_condition: form.item_condition.trim() || null,
      isbn: form.type === "book" && form.isbn.trim() ? form.isbn.trim() : null,
      measurements: form.type === "furniture" && form.measurements.trim() ? form.measurements.trim() : null,
    };

    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch("http://localhost:8000/listings/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "Authorization": `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to create listing");
      }

      const created = await res.json();
      onCreated(created);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Post a Listing</h2>
          <button className={styles.closeButton} onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.row}>
            <div className={styles.field}>
              <label className={styles.label}>Category</label>
              <select name="type" value={form.type} onChange={handleChange} className={styles.input}>
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
            <button type="button" className={styles.cancelButton} onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className={styles.submitButton} disabled={submitting}>
              {submitting ? "Posting..." : "Post Listing"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Market() {
  const [items, setItems] = useState([]);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    async function fetchListings() {
      try {
        const response = await fetch("http://localhost:8000/listings/?status=active");
        const data = await response.json();
        setItems(data);
      } catch (error) {
        console.error("Error fetching listings:", error);
      }
    }
    fetchListings();
  }, []);

  function handleCreated(newListing) {
    setItems((prev) => [newListing, ...prev]);
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Market</h1>

      <div className={styles.grid}>
        {/* Add listing card — always first */}
        <div className={styles.addCard} onClick={() => setShowModal(true)}>
          <div className={styles.addIcon}>+</div>
          <p className={styles.addTitle}>Sell Something</p>
          <p className={styles.addSubtitle}>Post your item to the marketplace</p>
        </div>

        {items.map((item) => (
          <ItemCard
            key={item.id}
            id={item.id}
            title={item.title}
            description={item.description}
            image={item.image}
          />
        ))}
      </div>

      {showModal && (
        <CreateListingModal
          onClose={() => setShowModal(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}

export default Market;
