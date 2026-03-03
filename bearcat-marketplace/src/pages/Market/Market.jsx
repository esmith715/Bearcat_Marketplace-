import ItemCard from "../../components/itemcard/ItemCard.jsx";
import { useEffect, useState } from "react";
import styles from "./Market.module.css";

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
		<div className={styles.container}>
			<h1 className={styles.title}>Market Page</h1>

			<div className={styles.grid}>
				{items.map((item) => (
					<ItemCard
						key={item.id}
						id={item.id}
						title={item.title}
						description={item.description}
						image={item.image}
					/>
				))}
			</div>
		</div>
	);
}

export default Market;
