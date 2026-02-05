import { Routes, Route } from "react-router-dom"
import './App.css'
import Navbar from "./components/navbar/Navbar.jsx"
import Home from './pages/Home.jsx'
import Market from './pages/Market.jsx'

function App() {

  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/market" element={<Market />} />
      </Routes>
      
    </>
  )
}

export default App
