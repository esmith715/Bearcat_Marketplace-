import styles from "./MyListingsTab.module.css";
import UserListings from "../../pages/Profile/UserListings";

export default function MyListingsTab({ isOpen, onClose }) {
  // Don't render anything at all when the tab is closed.
  // This also means the fetch inside UserListings won't fire
  // until the user actually opens this tab — good for performance.
  if (!isOpen) return null;

  return (
    // Backdrop — clicking outside the panel closes it,
    // same pattern as MessagesTab.
    <div className={styles.backdrop} onClick={onClose}>
      {/* stopPropagation prevents clicks inside the panel from
          bubbling up to the backdrop and closing it accidentally. */}
      <div
        className={styles.panel}
        onClick={(e) => e.stopPropagation()}
      >
        {/* ── Header ── */}
        <div className={styles.header}>
          <h2 className={styles.title}>🏷️ My Listings</h2>
          <button
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Close my listings"
          >
            ✕
          </button>
        </div>

        {/* ── Content ── */}
        {/* UserListings already handles its own loading, error,
            empty state, edit modal, delete, and view navigation.
            We get all of that for free by just rendering it here. */}
        <div className={styles.content}>
          <UserListings />
        </div>
      </div>
    </div>
  );
}