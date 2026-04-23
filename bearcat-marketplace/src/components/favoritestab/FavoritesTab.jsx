import styles from "./FavoritesTab.module.css";
import FavoriteListings from "../../pages/Profile/FavoriteListings";

export default function FavoritesTab({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div
        className={styles.panel}
        onClick={(e) => e.stopPropagation()}
      >
        {/* ── Header ── */}
        <div className={styles.header}>
          <h2 className={styles.title}>❤️ Favorites</h2>
          <button
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Close favorites"
          >
          </button>
        </div>

        {/* ── Content ── */}
        {/* FavoriteListings handles its own fetch, remove favorite,
            view navigation, loading/error/empty states. All reused. */}
        <div className={styles.content}>
          <FavoriteListings />
        </div>
      </div>
    </div>
  );
}