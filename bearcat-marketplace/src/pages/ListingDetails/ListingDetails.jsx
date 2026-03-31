import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import styles from "./ListingDetails.module.css";

function formatPrice(cents) {
  if (cents == null) return "N/A";
  return "$" + (cents / 100).toFixed(2);
}

function formatDate(iso) {
  if (!iso) return "N/A";
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function capitalize(str) {
  if (!str) return "N/A";
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function ListingDetails() {
  const { id } = useParams();
  const [listing, setListing] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchListing() {
      try {
        const res = await fetch(`http://localhost:8000/listings/${id}`);
        if (!res.ok) throw new Error("Listing not found");
        const data = await res.json();
        setListing(data);
      } catch (err) {
        setError(err.message);
      }
    }
    fetchListing();
  }, [id]);

  if (error) {
    return (
      <div className={styles.container}>
        <Link className={styles.backLink} to="/market">← Back to Market</Link>
        <p className={styles.error}>{error}</p>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className={styles.container}>
        <Link className={styles.backLink} to="/market">← Back to Market</Link>
        <p className={styles.loading}>Loading...</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <Link className={styles.backLink} to="/market">← Back to Market</Link>

      <div className={styles.card}>
        <div className={styles.header}>
          <div className={styles.badges}>
            <span className={`${styles.badge} ${styles[listing.type]}`}>
              {capitalize(listing.type)}
            </span>
            <span className={`${styles.badge} ${styles[listing.status]}`}>
              {capitalize(listing.status)}
            </span>
          </div>
          <h1 className={styles.title}>{listing.title}</h1>
          <p className={styles.price}>{formatPrice(listing.price_cents)}</p>
        </div>

        <div className={styles.divider} />

        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Description</h2>
          <p className={styles.description}>
            {listing.description || "No description provided."}
          </p>
        </div>

        <div className={styles.divider} />

        <div className={styles.details}>
          <div className={styles.detailRow}>
            <span className={styles.label}>Condition</span>
            <span className={styles.value}>{capitalize(listing.item_condition)}</span>
          </div>
          {listing.type === "book" && listing.isbn && (
            <div className={styles.detailRow}>
              <span className={styles.label}>ISBN</span>
              <span className={styles.value}>{listing.isbn}</span>
            </div>
          )}
          {listing.type === "furniture" && listing.measurements && (
            <div className={styles.detailRow}>
              <span className={styles.label}>Measurements</span>
              <span className={styles.value}>{listing.measurements}</span>
            </div>
          )}
          <div className={styles.detailRow}>
            <span className={styles.label}>Posted</span>
            <span className={styles.value}>{formatDate(listing.created_at)}</span>
          </div>
        </div>

        <div className={styles.actions}>
          <button
            className={styles.buyButton}
            onClick={() => alert(`Purchase flow for "${listing.title}" coming soon!`)}
            disabled={listing.status !== "active"}
          >
            {listing.status === "active" ? "Purchase Item" : capitalize(listing.status)}
          </button>
          <button
            className={styles.contactButton}
            onClick={() => alert(`Contact seller for "${listing.title}" coming soon!`)}
          >
            Contact Seller
          </button>
        </div>
      </div>
    </div>
  );
}
