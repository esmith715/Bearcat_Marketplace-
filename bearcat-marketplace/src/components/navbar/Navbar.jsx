import { Link, useNavigate } from 'react-router-dom'
import styles from './Navbar.module.css'
import logo from "../../assets/cropped-logo.png";

function Navbar() {
  const isLoggedIn = !!localStorage.getItem("access_token");

  return (
    <nav className={styles.nav}>
      <img className={styles.img} src={logo} alt="Bearcat Logo" />
      <Link className={styles.link} to="/">Home</Link>
      <Link className={styles.link} to="/market">Market</Link>
      <Link className={styles.link} to="/login">Login</Link>
      <Link className={styles.link} to="/profile">Profile</Link>
    </nav>
  )
}

export default Navbar
