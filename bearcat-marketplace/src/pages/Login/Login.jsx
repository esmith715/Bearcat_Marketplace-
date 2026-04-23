import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import styles from "./Login.module.css";

export default function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState("login"); // "login" | "register"

  useEffect(() => {
    if (searchParams.get("mode") === "register") {
      setMode("register");
    }
  }, [searchParams]);

  // Login fields
  const [loginForm, setLoginForm] = useState({ email_or_username: "", password: "" });

  // Register fields
  const [registerForm, setRegisterForm] = useState({ email: "", username: "", password: "", confirm: "" });

  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  function switchMode(newMode) {
    setMode(newMode);
    setError(null);
    setSuccessMsg(null);
  }

  // ── Login ──────────────────────────────────────────────
  async function handleLogin(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginForm),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Login failed");
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      window.dispatchEvent(new Event("authChange"));
      navigate("/market");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // ── Register ───────────────────────────────────────────
  async function handleRegister(e) {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);

    if (registerForm.password !== registerForm.confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: registerForm.email,
          username: registerForm.username,
          password: registerForm.password,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Registration failed");
      }

      // Step 2: Automatically send the verification email
      // We fire-and-forget this — if it fails, the user can request
      // a new one later. We don't block registration on email delivery.
      fetch(
        `http://localhost:8000/auth/send-verification-email?email=${encodeURIComponent(registerForm.email)}`,
        { method: "POST" }
      ).catch(() => {}); // silently ignore email send failures

      setSuccessMsg(
      "Account created! Check your email for a verification link, then log in."
      );
      switchMode("login");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>

        {/* Tab toggle */}
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${mode === "login" ? styles.activeTab : ""}`}
            onClick={() => switchMode("login")}
            type="button"
          >
            Log In
          </button>
          <button
            className={`${styles.tab} ${mode === "register" ? styles.activeTab : ""}`}
            onClick={() => switchMode("register")}
            type="button"
          >
            Sign Up
          </button>
        </div>

        {successMsg && <p className={styles.success}>{successMsg}</p>}
        {error && <p className={styles.error}>{error}</p>}

        {/* ── Login Form ── */}
        {mode === "login" && (
          <form onSubmit={handleLogin} className={styles.form}>
            <div className={styles.field}>
              <label className={styles.label}>Email or Username</label>
              <input
                className={styles.input}
                type="text"
                placeholder="bearcatstudent or name@mail.uc.edu"
                value={loginForm.email_or_username}
                onChange={(e) => setLoginForm({ ...loginForm, email_or_username: e.target.value })}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Password</label>
              <input
                className={styles.input}
                type="password"
                placeholder="••••••••"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                required
              />
            </div>
            <a href="/forgot-password" className={styles.forgotLink}>
              Forgot password?
            </a>
            <button className={styles.primaryButton} type="submit" disabled={loading}>
              {loading ? "Logging in..." : "Log In"}
            </button>
          </form>
        )}

        {/* ── Register Form ── */}
        {mode === "register" && (
          <form onSubmit={handleRegister} className={styles.form}>
            <div className={styles.field}>
              <label className={styles.label}>UC Email</label>
              <input
                className={styles.input}
                type="email"
                placeholder="name@mail.uc.edu"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Username</label>
              <input
                className={styles.input}
                type="text"
                placeholder="bearcatstudent"
                value={registerForm.username}
                onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Password</label>
              <input
                className={styles.input}
                type="password"
                placeholder="••••••••"
                value={registerForm.password}
                onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Confirm Password</label>
              <input
                className={styles.input}
                type="password"
                placeholder="••••••••"
                value={registerForm.confirm}
                onChange={(e) => setRegisterForm({ ...registerForm, confirm: e.target.value })}
                required
              />
            </div>

            <p className={styles.hint}>Must be a UC email address (@mail.uc.edu)</p>

            <button className={styles.primaryButton} type="submit" disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </button>
          </form>
        )}

      </div>
    </div>
  );
}
