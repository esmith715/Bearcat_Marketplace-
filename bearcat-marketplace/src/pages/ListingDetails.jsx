import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

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
    <div style={{ padding: "20px" }}>
      <Link to="/market">← Back to Market</Link>
      <h1>Listing Details</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {!listing && !error && <p>Loading...</p>}

      {listing && (
        <pre style={{ background: "#f5f5f5", padding: "15px" }}>
          {JSON.stringify(listing, null, 2)}
        </pre>
      )}
    </div>
  );
}