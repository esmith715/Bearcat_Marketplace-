import { useEffect, useRef, useState } from "react";
import { useWebSocket } from "../../hooks/useWebSocket";
import styles from "./NotificationBell.module.css";

const API = "http://localhost:8000";

function timeAgo(isoString) {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function notificationLabel(n) {
  switch (n.type) {
    case "new_message":
      return "💬 You have a new message";
    case "listing_updated":
      return "📝 A listing you follow was updated";
    case "listing_sold":
      return "🏷️ A listing was marked as sold";
    default:
      return "🔔 New notification";
  }
}

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  const token = localStorage.getItem("access_token");

  // Fetch unread count on mount
  useEffect(() => {
    if (!token) return;
    fetch(`${API}/notifications/unread-count`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((d) => setUnreadCount(d.unread_count ?? 0))
      .catch(() => {});
  }, [token]);

  // Listen for real-time notifications via WebSocket
  useWebSocket((data) => {
    if (data.type === "notification") {
      setUnreadCount((c) => c + 1);
      setNotifications((prev) => [data.notification, ...prev]);
    }
  });

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleOpen() {
    if (!token) return;
    setOpen((prev) => !prev);

    if (!open) {
      setLoading(true);
      try {
        const res = await fetch(`${API}/notifications/?limit=20`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setNotifications(Array.isArray(data) ? data : []);
      } catch {
        setNotifications([]);
      } finally {
        setLoading(false);
      }
    }
  }

  async function markAllRead() {
    if (!token) return;
    await fetch(`${API}/notifications/read-all`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
    });
    setUnreadCount(0);
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  }

  async function markOneRead(id) {
    if (!token) return;
    await fetch(`${API}/notifications/${id}/read`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
    });
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );
    setUnreadCount((c) => Math.max(0, c - 1));
  }

  if (!token) return null;

  return (
    <div className={styles.wrapper} ref={dropdownRef}>
      <button
        className={styles.bellButton}
        onClick={handleOpen}
        aria-label="Notifications"
        title="Notifications"
      >
        <svg
          className={styles.bellIcon}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        {unreadCount > 0 && (
          <span className={styles.badge}>
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className={styles.dropdown}>
          <div className={styles.dropdownHeader}>
            <span className={styles.dropdownTitle}>Notifications</span>
            {unreadCount > 0 && (
              <button className={styles.markAllBtn} onClick={markAllRead}>
                Mark all read
              </button>
            )}
          </div>

          <div className={styles.list}>
            {loading && (
              <div className={styles.empty}>Loading...</div>
            )}
            {!loading && notifications.length === 0 && (
              <div className={styles.empty}>You're all caught up! 🎉</div>
            )}
            {!loading &&
              notifications.map((n) => (
                <div
                  key={n.id}
                  className={`${styles.item} ${!n.is_read ? styles.unread : ""}`}
                  onClick={() => !n.is_read && markOneRead(n.id)}
                >
                  <div className={styles.itemText}>{notificationLabel(n)}</div>
                  <div className={styles.itemTime}>{timeAgo(n.created_at)}</div>
                  {!n.is_read && <span className={styles.dot} />}
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}