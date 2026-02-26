import ItemCard from "../components/itemcard/ItemCard.jsx";
import { useEffect, useState } from "react";

function Market() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    async function fetchListings() {
      try {
        const response = await fetch("http://localhost:8000/listings/");
        const data = await response.json();
        setItems(data);
      } catch (error) {
        console.error("Error fetching listings:", error);
      }
    }

    fetchListings();
  }, []);
  
  return (
    <>
      <h1>Market Page</h1>

      <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
        {items.map((item, index) => (
          <ItemCard
            key={item.id}
            title={item.title}
            description={item.description}
          />
        ))}
      </div>
    </>
  );
}

export default Market;
