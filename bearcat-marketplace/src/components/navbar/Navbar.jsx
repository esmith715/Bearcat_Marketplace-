import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import styles from "./Navbar.module.css";
import logo from "../../assets/cropped-logo.png";
import NotificationBell from "../notificationbell/NotificationBell";

function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("access_token")
  );

  const [unreadMessages, setUnreadMessages] = useState(0);
  // ── LISTEN FOR LOGIN/LOGOUT EVENTS ACROSS TABS ──────────────────────────
  // Here's a subtle but important problem:
  // If the user logs in on the Login PAGE, that page updates localStorage.
  // But the Navbar is a DIFFERENT component — it won't automatically know
  // that localStorage changed, because useState only re-renders THIS component
  // when WE call setIsLoggedIn().
  //
  // The browser has a built-in event called "storage" that fires whenever
  // localStorage changes — but only in OTHER tabs, not the current one.
  // For changes in the SAME tab, we use a custom event (see Login page section below).
  //
  // useEffect with [] runs once when the component first appears (mounts).
  // We use it to set up event listeners.
  useEffect(() => {
    // This function runs whenever our custom "authChange" event is fired.
    // We'll fire this event from the Login page after a successful login.
    function handleAuthChange() {
      setIsLoggedIn(!!localStorage.getItem("access_token"));
    }

    window.addEventListener("authChange", handleAuthChange);

    // The "storage" event fires when localStorage changes in ANOTHER tab.
    // This handles the case where the user logs in/out in a different tab.
    window.addEventListener("storage", handleAuthChange);

    return () => {
      window.removeEventListener("authChange", handleAuthChange);
      window.removeEventListener("storage", handleAuthChange);
    };
  }, []);

  // ── FETCH UNREAD MESSAGE COUNT ─────────────────────────────────────────────
  // Poll the unread count endpoint every 30 seconds so the badge stays fresh.
  // We also re-fetch whenever isLoggedIn changes (e.g., right after login).
  useEffect(() => {
    // If not logged in, reset the badge and stop
    if (!isLoggedIn) {
      setUnreadMessages(0);
      return;
    }

    async function fetchUnreadCount() {
      const token = localStorage.getItem("access_token");
      if (!token) return;
      try {
        const res = await fetch(
          "http://localhost:8000/messages/unread-count-total",
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (res.ok) {
          const data = await res.json();
          // data is: { "unread_count": 3 }
          setUnreadMessages(data.unread_count ?? 0);
        }
      } catch {
        // Silently ignore — a failed badge fetch shouldn't break the navbar
      }
    }

    fetchUnreadCount(); // Fetch immediately on mount / login

    // setInterval runs fetchUnreadCount every 30 seconds (30,000 ms)
    // This is like a background thread that keeps the badge up to date
    const interval = setInterval(fetchUnreadCount, 30_000);

    // Cleanup: clear the interval when the component unmounts or isLoggedIn changes
    // Without this, the interval would keep running and cause memory leaks
    return () => clearInterval(interval);
  }, [isLoggedIn]);

  // ── LOGOUT HANDLER ───────────────────────────────────────────────────────
  // This function runs when the user clicks the Log out button.
   function handleLogout() {
    // Step 1: Remove the auth tokens from localStorage.
    // Without a valid token, the backend will reject all authenticated requests.
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    // Step 2: Update Navbar's own state so it re-renders immediately.
    // Without this, the Navbar would still show "Profile" and "Log out"
    // until the next page load.
    setIsLoggedIn(false);

    // Step 3: Notify any other components listening for auth changes.
    // new Event("authChange") creates a browser event object with our custom name.
    // window.dispatchEvent() broadcasts it — any addEventListener("authChange")
    // anywhere on the page will receive it.
    window.dispatchEvent(new Event("authChange"));

    // Step 4: Redirect to home page.
    // We use window.location.href instead of useNavigate() here because
    // it's simpler and guaranteed to work regardless of Router context.
    // The trade-off: this does a full page reload (like clicking a link),
    // whereas useNavigate() would do a smooth client-side navigation.
    // For a logout action, a full reload is actually desirable — it clears
    // any in-memory state from other components too (a clean slate).
    window.location.href = "/";
  }

  return (
    <nav className={styles.nav} aria-label="Main">
      <div className={styles.left}>
        <Link to="/" className={styles.logoLink}>
          <img className={styles.img} src={logo} alt="Bearcat Marketplace" />
        </Link>

        <div className={styles.navLinks}>
          <Link className={styles.link} to="/">
            Home
          </Link>
          <Link className={styles.link} to="/market">
            Market
          </Link>
          <Link className={styles.link} to="/messages">
            <span className={styles.linkInner}>
              Messages
              {unreadMessages > 0 && (
                <span className={styles.msgBadge}>
                  {unreadMessages > 99 ? "99+" : unreadMessages}
                </span>
              )}
            </span>
          </Link>
          <Link className={styles.link} to="/my-listings">My Listings</Link>
          <Link className={styles.link} to="/favorites">Favorites</Link>
        </div>
      </div>

      <div className={styles.right}>
        {isLoggedIn ? (
          <>
            <NotificationBell />

            <Link className={styles.profileBtn} to="/profile">
              Profile
            </Link>

            <button className={styles.logoutBtn} onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <Link className={styles.outlineBtn} to="/login">
            Log in
          </Link>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
