import { Link } from "react-router-dom";
import styles from "./Navbar.module.css";
import logo from "../../assets/cropped-logo.png";

function Navbar() {
  const isLoggedIn = !!localStorage.getItem("access_token");

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
        </div>
      </div>

      <div className={styles.right}>
        {isLoggedIn ? (
          <Link className={styles.profileBtn} to="/profile">
            Profile
          </Link>
        ) : (
          <>
            <Link className={styles.outlineBtn} to="/login">
              Log in
            </Link>
            <Link className={styles.primaryBtn} to="/login?mode=register">
              Sign up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
