import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import styles from "./VerifyEmail.module.css";

// The three states this page can be in
const STATUS = {
  LOADING:  "loading",
  SUCCESS:  "success",
  ERROR:    "error",
};

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token          = searchParams.get("token");
  const [status, setStatus] = useState(STATUS.LOADING);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    // No token in the URL — nothing to verify
    if (!token) {
      setErrorMsg("No verification token found in the link.");
      setStatus(STATUS.ERROR);
      return;
    }

    // Fire the verification request immediately on page load
    async function verify() {
      try {
        const res = await fetch(
          `http://localhost:8000/auth/verify-email?token=${encodeURIComponent(token)}`,
          { method: "POST" }
        );

        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || "Verification failed.");
        }

        setStatus(STATUS.SUCCESS);

      } catch (err) {
        setErrorMsg(err.message);
        setStatus(STATUS.ERROR);
      }
    }

    verify();
  }, [token]); // only runs once when the token is read from the URL

  return (
    <div className={styles.page}>
      <div className={styles.card}>

        {/* ── Loading ── */}
        {status === STATUS.LOADING && (
          <>
            <div className={styles.spinner} />
            <p className={styles.message}>Verifying your email…</p>
          </>
        )}

        {/* ── Success ── */}
        {status === STATUS.SUCCESS && (
          <>
            <span className={styles.icon}>🎉</span>
            <h1 className={styles.title}>Email Verified!</h1>
            <p className={styles.message}>
              Your UC email has been verified. You're all set to start buying
              and selling on Bearcat Marketplace!
            </p>
            <Link to="/login" className={styles.primaryButton}>
              Log In
            </Link>
          </>
        )}

        {/* ── Error ── */}
        {status === STATUS.ERROR && (
          <>
            <span className={styles.icon}>❌</span>
            <h1 className={styles.title}>Verification Failed</h1>
            <p className={styles.message}>{errorMsg}</p>
            <p className={styles.hint}>
              Your link may have expired (links are valid for 24 hours).
              You can request a new one from your profile page after logging in.
            </p>
            <Link to="/login" className={styles.primaryButton}>
              Back to Log In
            </Link>
          </>
        )}

      </div>
    </div>
  );
}