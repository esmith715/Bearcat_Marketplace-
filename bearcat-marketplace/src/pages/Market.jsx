import ItemCard from "../components/itemcard/ItemCard.jsx";
import items from "../components/itemcard/ItemCard.json";



function Market() {
  return (
    <>
      <h1>Market Page</h1>

      <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
        {items.map((item, index) => (
          <ItemCard
            key={index}
            title={item.title}
            description={item.description}
            image={item.image}
          />
        ))}
      </div>
    </>
  );
}

export default Market;
