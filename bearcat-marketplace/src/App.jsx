import { Routes, Route } from "react-router-dom"
import './App.css'
import Navbar from "./components/navbar/Navbar.jsx"
import Home from './pages/Home/Home.jsx'
import Market from './pages/Market/Market.jsx'
import Login from './pages/Login/Login.jsx'
import ListingDetails from "./pages/ListingDetails/ListingDetails.jsx"
import Profile from "./pages/Profile/Profile.jsx"
import AdminReports from "./pages/AdminReports/AdminReports.jsx"

function App() {

  return (
    <>
      <Navbar />
      <main className="app-container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/market" element={<Market />} />
          <Route path="/login" element={<Login />} />
          <Route path="/market/:id" element={<ListingDetails />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/admin/reports" element={<AdminReports />} />
        </Routes>
      </main>
    </>
  )
}

export default App
