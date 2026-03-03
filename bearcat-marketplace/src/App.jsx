import { Routes, Route } from "react-router-dom"
import './App.css'
import Navbar from "./components/navbar/Navbar.jsx"
import Home from './pages/Home/Home.jsx'
import Market from './pages/Market/Market.jsx'
import ListingDetails from "./pages/ListingDetails/ListingDetails.jsx"

function App() {

  return (
    <>
      <Navbar />
      <main className="app-container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/market" element={<Market />} />
          <Route path="/market/:id" element={<ListingDetails />} />
        </Routes>
      </main>
    </>
  )
}

export default App
