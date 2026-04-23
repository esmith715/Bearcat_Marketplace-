import { useState } from "react";
import { Link } from "react-router-dom";
import styles from "./ForgotPassword.module.css";

export default function ForgotPassword() {
  const [email, setEmail]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [success, setSuccess]   = useState(false);
  const [error, setError]       = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(
        `http://localhost:8000/auth/request-password-reset?email=${encodeURIComponent(email)}`,
        { method: "POST" }
      );

      // IMPORTANT: We always show the success message even if the email
      // doesn't exist in our system. This prevents user enumeration attacks
      // (i.e. someone fishing to find out which emails are registered).
      setSuccess(true);

    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Forgot Password</h1>

        {success ? (
          // ── Success state ──────────────────────────────────────────────
          <div className={styles.successBox}>
            <span className={styles.successIcon}>📬</span>
            <p className={styles.successText}>
              If that email is registered, you'll receive a reset link shortly.
              Check your inbox (and spam folder, just in case).
            </p>
            <Link to="/login" className={styles.backLink}>
              ← Back to Log In
            </Link>
          </div>
        ) : (
          // ── Form state ─────────────────────────────────────────────────
          <>
            <p className={styles.subtitle}>
              Enter your UC email and we'll send you a link to reset your password.
            </p>

            {error && <p className={styles.error}>{error}</p>}

            <form onSubmit={handleSubmit} className={styles.form}>
              <div className={styles.field}>
                <label className={styles.label}>UC Email</label>
                <input
                  className={styles.input}
                  type="email"
                  placeholder="name@mail.uc.edu"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoFocus
                />
              </div>

              <button
                className={styles.primaryButton}
                type="submit"
                disabled={loading}
              >
                {loading ? "Sending…" : "Send Reset Link"}
              </button>
            </form>

            <Link to="/login" className={styles.backLink}>
              ← Back to Log In
            </Link>
          </>
        )}
      </div>
    </div>
  );
}