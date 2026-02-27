import {Link} from 'react-router-dom'
import './Navbar.css'
import logo from "../../assets/cropped-logo.png";

function Navbar() {
  return (
    <>
      <nav>
        <img src={logo} alt="Bearcat Logo" />
        <Link className="link" to="/">Home</Link>
        <Link className="link" to="/market">Market</Link>
      </nav>
    </>
  )
}

export default Navbar