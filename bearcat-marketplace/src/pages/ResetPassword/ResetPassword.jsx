import { useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import styles from "./ResetPassword.module.css";

export default function ResetPassword() {
  const [searchParams]          = useSearchParams();
  const token                   = searchParams.get("token");

  const [newPassword, setNewPassword]       = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading]               = useState(false);
  const [success, setSuccess]               = useState(false);
  const [error, setError]                   = useState(null);

  // If there's no token in the URL, the link is broken/missing
  if (!token) {
    return (
      <div className={styles.page}>
        <div className={styles.card}>
          <span className={styles.icon}>⚠️</span>
          <h1 className={styles.title}>Invalid Link</h1>
          <p className={styles.subtitle}>
            This password reset link is missing or malformed.
            Please request a new one.
          </p>
          <Link to="/forgot-password" className={styles.primaryButton}>
            Request New Link
          </Link>
        </div>
      </div>
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (newPassword.length < 4) {
      setError("Password must be at least 4 characters.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(
        `http://localhost:8000/auth/reset-password?password_reset_token=${encodeURIComponent(token)}&new_password=${encodeURIComponent(newPassword)}`,
        { method: "POST" }
      );

      const data = await res.json();

      if (!res.ok) {
        // Common case: token expired or already used
        throw new Error(data.detail || "Reset failed. Your link may have expired.");
      }

      setSuccess(true);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Reset Password</h1>

        {success ? (
          // ── Success state ──────────────────────────────────────────────
          <div className={styles.successBox}>
            <span className={styles.icon}>✅</span>
            <p className={styles.successText}>
              Your password has been reset successfully!
            </p>
            <Link to="/login" className={styles.primaryButton}>
              Log In
            </Link>
          </div>
        ) : (
          // ── Form state ─────────────────────────────────────────────────
          <>
            <p className={styles.subtitle}>Enter your new password below.</p>

            {error && <p className={styles.error}>{error}</p>}

            <form onSubmit={handleSubmit} className={styles.form}>
              <div className={styles.field}>
                <label className={styles.label}>New Password</label>
                <input
                  className={styles.input}
                  type="password"
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  autoFocus
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Confirm Password</label>
                <input
                  className={styles.input}
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>

              <button
                className={styles.primaryButton}
                type="submit"
                disabled={loading}
              >
                {loading ? "Resetting…" : "Reset Password"}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}