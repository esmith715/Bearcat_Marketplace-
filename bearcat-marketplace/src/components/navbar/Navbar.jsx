import {Link} from 'react-router-dom'
import './Navbar.css'

function Navbar() {
  return (
    <>
      <nav>
        <img src="/src/assets/logo.png" alt="Bearcat Logo" />
        <Link className="link" to="/">Home</Link>
        <Link className="link" to="/market">Market</Link>
      </nav>
    </>
  )
}

export default Navbar