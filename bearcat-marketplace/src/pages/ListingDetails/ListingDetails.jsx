import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import styles from "./ListingDetails.module.css";

export default function ListingDetails() {
	const { id } = useParams();
	const [listing, setListing] = useState(null);
	const [error, setError] = useState(null);

	useEffect(() => {
		async function fetchListing() {
			try {
				const res = await fetch(`http://localhost:8000/listings/${id}`);
				if (!res.ok) {
					throw new Error("Listing not found");
				}
				const data = await res.json();
				setListing(data);
			} catch (err) {
				setError(err.message);
			}
		}

		fetchListing();
	}, [id]);

	return (
		<div className={styles.container}>
			<Link className={styles.backLink} to="/market">← Back to Market</Link>
			<h1 className={styles.title}>Listing Details</h1>

			{error && <p className={styles.error}>{error}</p>}
			{!listing && !error && <p>Loading...</p>}

			{listing && (
				<pre className={styles.pre}>
					{JSON.stringify(listing, null, 2)}
				</pre>
			)}
		</div>
	);
}
