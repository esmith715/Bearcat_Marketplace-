import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./UserListings.module.css";
import EditListingModal from "../../components/editlistingmodal/EditListingModal";

export default function UserListings() {
  const navigate = useNavigate();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingListing, setEditingListing] = useState(null);

  useEffect(() => {
    async function fetchMyListings() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const res = await fetch("http://localhost:8000/listings/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.status === 401) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          setListings([]);
          setLoading(false);
          return;
        }

        if (!res.ok) {
          throw new Error("Failed to load your listings");
        }

        const data = await res.json();
        setListings(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchMyListings();
  }, []);

  function formatPrice(priceCents) {
    return `$${(priceCents / 100).toFixed(2)}`;
  }

  function formatDate(iso) {
    return new Date(iso).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  async function handleDelete(listingId) {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    const confirmed = window.confirm("Delete this listing?");
    if (!confirmed) return;

    try {
      const res = await fetch(`http://localhost:8000/listings/${listingId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to delete listing");
      }

      setListings((prev) => prev.filter((listing) => listing.id !== listingId));
    } catch (err) {
      setError(err.message);
    }
  }

  function handleEdit(listing) {
    setEditingListing(listing);
  }

  function handleView(listingId) {
    navigate(`/market/${listingId}`, {
        state: { from: "profile" }
    });
  }

  function handleUpdatedListing(updatedListing) {
    setListings((prev) =>
        prev.map((listing) =>
        listing.id === updatedListing.id ? updatedListing : listing
        )
    );
  }

  return (
    <>
    <section className={styles.section}>
      <div className={styles.headerRow}>
        <h2 className={styles.title}>Your Listings</h2>
        <span className={styles.count}>{listings.length}</span>
      </div>

      {/* all your existing listings UI here */}
      {loading ? (
        <p className={styles.message}>Loading your listings...</p>
      ) : error ? (
        <p className={styles.error}>{error}</p>
      ) : listings.length === 0 ? (
        <div className={styles.emptyState}>
          <p className={styles.emptyTitle}>No listings yet</p>
          <p className={styles.emptyText}>
            Listings you create will appear here.
          </p>
        </div>
      ) : (
        <div className={styles.scrollArea}>
          {listings.map((listing) => (
            <article key={listing.id} className={styles.card}>
                <div className={styles.topRow}>
                <div className={styles.mainInfo}>
                    <h3 className={styles.listingTitle}>{listing.title}</h3>
                    <p className={styles.meta}>
                    {listing.type} • {listing.item_condition || "No condition"}
                    </p>
                </div>

                <div className={styles.rightInfo}>
                    <div className={styles.price}>
                    {formatPrice(listing.price_cents)}
                    </div>
                    <span
                    className={`${styles.status} ${
                        styles[`status_${listing.status}`]
                    }`}
                    >
                    {listing.status}
                    </span>
                </div>
                </div>

                {listing.description && (
                <p className={styles.description}>{listing.description}</p>
                )}

                <div className={styles.bottomRow}>
                <span className={styles.date}>
                    Created {formatDate(listing.created_at)}
                </span>

                <div className={styles.actions}>
                    <button
                        type="button"
                        className={styles.viewButton}
                        onClick={() => handleView(listing.id)}
                    >
                        View Details
                    </button>

                    <button
                        type="button"
                        className={styles.editButton}
                        onClick={() => handleEdit(listing)}
                    >
                        Edit
                    </button>

                    <button
                        type="button"
                        className={styles.deleteButton}
                        onClick={() => handleDelete(listing.id)}
                    >
                        Remove
                    </button>
                </div>
                </div>
            </article>
            ))}
        </div>
      )}
    </section>

    {/* 👇 ADD IT HERE (outside section, but inside return) */}
    {editingListing && (
      <EditListingModal
        listing={editingListing}
        onClose={() => setEditingListing(null)}
        onUpdated={handleUpdatedListing}
      />
    )}
   </>
  );
}
