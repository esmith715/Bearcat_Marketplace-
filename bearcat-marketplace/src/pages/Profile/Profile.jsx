import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Profile.module.css";

export default function Profile() {
  const navigate = useNavigate(); // used by logout
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchMe() {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      try {
        const res = await fetch("http://localhost:8000/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (res.status === 401) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          return;
        }

        if (!res.ok) throw new Error("Failed to load profile");

        const data = await res.json();
        setUser(data);
      } catch (err) {
        setError(err.message);
      }
    }

    fetchMe();
  }, []);

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login");
  }

  function formatDate(iso) {
    return new Date(iso).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  if (error) return <div className={styles.container}><p className={styles.error}>{error}</p></div>;

  if (!user) return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.empty}>
          <div className={styles.emptyAvatar}>?</div>
          <p className={styles.emptyText}>Not logged in</p>
          <p className={styles.emptySubtext}>Log in to view your profile</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className={styles.container}>
      <div className={styles.card}>

        {/* Avatar + name */}
        <div className={styles.avatarSection}>
          <div className={styles.avatar}>
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className={styles.username}>{user.username}</h1>
            <span className={`${styles.roleBadge} ${user.role === "admin" ? styles.admin : styles.student}`}>
              {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
            </span>
          </div>
        </div>

        <div className={styles.divider} />

        {/* Info rows */}
        <div className={styles.infoSection}>
          <div className={styles.row}>
            <span className={styles.label}>Email</span>
            <span className={styles.value}>{user.email}</span>
          </div>
          <div className={styles.row}>
            <span className={styles.label}>Email Verified</span>
            <span className={`${styles.value} ${user.is_email_verified ? styles.verified : styles.unverified}`}>
              {user.is_email_verified ? "Verified" : "Not verified"}
            </span>
          </div>
          <div className={styles.row}>
            <span className={styles.label}>Member Since</span>
            <span className={styles.value}>{formatDate(user.created_at)}</span>
          </div>
        </div>

        <div className={styles.divider} />

        <button className={styles.logoutButton} onClick={handleLogout}>
          Log Out
        </button>

      </div>
    </div>
  );
}
