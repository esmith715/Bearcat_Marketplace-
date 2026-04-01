import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./FavoriteListings.module.css";

export default function FavoriteListings() {
  const navigate = useNavigate();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchFavorites() {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const res = await fetch("http://localhost:8000/favorites/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          throw new Error("Failed to load favorite listings");
        }

        const data = await res.json();
        setListings(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchFavorites();
  }, []);

  async function handleRemoveFavorite(listingId) {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
      const res = await fetch(`http://localhost:8000/favorites/${listingId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to remove favorite");
      }

      setListings((prev) => prev.filter((listing) => listing.id !== listingId));
    } catch (err) {
      setError(err.message);
    }
  }

  function handleView(listingId) {
    navigate(`/market/${listingId}`, {
      state: { from: "profile" }
    });
  }

  function formatPrice(priceCents) {
    return `$${(priceCents / 100).toFixed(2)}`;
  }

  return (
    <section className={styles.section}>
      <div className={styles.headerRow}>
        <h2 className={styles.title}>Favorite Listings</h2>
        <span className={styles.count}>{listings.length}</span>
      </div>

      {loading ? (
        <p className={styles.message}>Loading favorites...</p>
      ) : error ? (
        <p className={styles.error}>{error}</p>
      ) : listings.length === 0 ? (
        <div className={styles.emptyState}>
          <p className={styles.emptyTitle}>No favorites yet</p>
          <p className={styles.emptyText}>Favorited listings will appear here.</p>
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

                <div className={styles.price}>
                  {formatPrice(listing.price_cents)}
                </div>
              </div>

              {listing.description && (
                <p className={styles.description}>{listing.description}</p>
              )}

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
                  className={styles.removeButton}
                  onClick={() => handleRemoveFavorite(listing.id)}
                >
                  Remove
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
