import { useEffect, useState } from "react";
import ItemCard from "../../components/itemcard/ItemCard.jsx";
import styles from "./Market.module.css";
import ListingForm from "../../components/listingform/ListingForm.jsx";

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
  async function handleCreate(payload) {
    const token = localStorage.getItem("access_token");

    const res = await fetch("http://localhost:8000/listings/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
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
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Post a Listing</h2>
          <button className={styles.closeButton} onClick={onClose}>✕</button>
        </div>

        <ListingForm
          onSubmit={handleCreate}
          onCancel={onClose}
          submitText="Post Listing"
          submittingText="Posting..."
        />
      </div>
    </div>
  );
}

function Market() {
  const [items, setItems] = useState([]);
  const [favoriteIds, setFavoriteIds] = useState([]);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const [listingsRes] = await Promise.all([
          fetch("http://localhost:8000/listings/?status=active"),
        ]);

        const listingsData = await listingsRes.json();
        setItems(listingsData);

        const token = localStorage.getItem("access_token");
        if (token) {
          const favoritesRes = await fetch("http://localhost:8000/favorites/me/ids", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (favoritesRes.ok) {
            const favoriteData = await favoritesRes.json();
            setFavoriteIds(favoriteData);
          }
        }
      } catch (error) {
        console.error("Error fetching listings:", error);
      }
    }

    fetchData();
  }, []);

  function handleCreated(newListing) {
    setItems((prev) => [newListing, ...prev]);
  }

  async function handleToggleFavorite(listingId, isFavorited) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      alert("Please log in to favorite listings.");
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/favorites/${listingId}`, {
        method: isFavorited ? "DELETE" : "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to update favorites");
      }

      setFavoriteIds((prev) =>
        isFavorited
          ? prev.filter((id) => id !== listingId)
          : [...prev, listingId]
      );
    } catch (error) {
      console.error("Error updating favorite:", error);
    }
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Market</h1>

      <div className={styles.grid}>
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
            isFavorited={favoriteIds.includes(item.id)}
            onToggleFavorite={handleToggleFavorite}
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
