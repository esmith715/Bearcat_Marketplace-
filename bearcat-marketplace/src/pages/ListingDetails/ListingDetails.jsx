import { useEffect, useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import styles from "./ListingDetails.module.css";
import { getImageSrc } from "../../utils/images";
import MessageBoard from "../../components/messageboard/MessageBoard";

function formatPrice(cents) {
  if (cents == null) return "N/A";
  return "$" + (cents / 100).toFixed(2);
}

function formatDate(iso) {
  if (!iso) return "N/A";
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function capitalize(str) {
  if (!str) return "N/A";
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function ListingDetails() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const from = location.state?.from;
  const [listing, setListing] = useState(null);
  const [error, setError] = useState(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState("");
  const [reportError, setReportError] = useState(null);
  const [reportSuccess, setReportSuccess] = useState(false);
  const [isReporting, setIsReporting] = useState(false);

  useEffect(() => {
    async function fetchListing() {
      try {
        const res = await fetch(`http://localhost:8000/listings/${id}`);
        if (!res.ok) throw new Error("Listing not found");
        const data = await res.json();
        setListing(data);
      } catch (err) {
        setError(err.message);
      }
    }
    fetchListing();
  }, [id]);

  function handleBack() {
    if (from === "profile") {
      navigate("/profile");
    } else {
      navigate("/market");
    }
  }

  async function handleReportSubmit(e) {
    e.preventDefault();
    setReportError(null);
    setIsReporting(true);

    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("You must be logged in to report a listing.");
      }

      const userRes = await fetch("http://localhost:8000/auth/me", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!userRes.ok) {
        throw new Error("Could not verify your identity. Please log in again.");
      }
      const user = await userRes.json();

      const reportRes = await fetch("http://localhost:8000/reports/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          listing_id: id,
          reporter_id: user.id,
          reason: reportReason
        })
      });

      if (!reportRes.ok) {
        throw new Error("Failed to submit report. Please try again.");
      }

      setReportSuccess(true);
      setTimeout(() => {
        setShowReportModal(false);
        setReportSuccess(false);
        setReportReason("");
      }, 2000);
    } catch (err) {
      setReportError(err.message);
    } finally {
      setIsReporting(false);
    }
  }

  if (error) {
    return (
      <div className={styles.container}>
        <button className={styles.backLink} onClick={handleBack}>
          {from === "profile" ? "← Back to Profile" : "← Back to Market"}
        </button>
        <p className={styles.error}>{error}</p>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className={styles.container}>
        <button className={styles.backLink} onClick={handleBack}>
          {from === "profile" ? "← Back to Profile" : "← Back to Market"}
        </button>
        <p className={styles.loading}>Loading...</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <button className={styles.backLink} onClick={handleBack}>
        {from === "profile" ? "← Back to Profile" : "← Back to Market"}
      </button>

      <div className={styles.card}>
        <div className={styles.header}>
          <div className={styles.badges}>
            <span className={`${styles.badge} ${styles[listing.type]}`}>
              {capitalize(listing.type)}
            </span>
            <span className={`${styles.badge} ${styles[listing.status]}`}>
              {capitalize(listing.status)}
            </span>
          </div>
          <h1 className={styles.title}>{listing.title}</h1>
          <p className={styles.price}>{formatPrice(listing.price_cents)}</p>
        </div>

        <div className={styles.divider} />

        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Description</h2>
          <p className={styles.description}>
            {listing.description || "No description provided."}
          </p>
        </div>

        {listing.image_url && (
          <>
            <div className={styles.divider} />
            <div className={styles.imageSection}>
              <img
                className={styles.listingImage}
                src={getImageSrc(listing.image_url)}
                alt={listing.title}
              />
            </div>
            <div className={styles.divider} />
          </>
        )}

        <div className={styles.divider} />

        <div className={styles.details}>
          <div className={styles.detailRow}>
            <span className={styles.label}>Condition</span>
            <span className={styles.value}>{capitalize(listing.item_condition)}</span>
          </div>
          {listing.type === "book" && listing.isbn && (
            <div className={styles.detailRow}>
              <span className={styles.label}>ISBN</span>
              <span className={styles.value}>{listing.isbn}</span>
            </div>
          )}
          {listing.type === "furniture" && listing.measurements && (
            <div className={styles.detailRow}>
              <span className={styles.label}>Measurements</span>
              <span className={styles.value}>{listing.measurements}</span>
            </div>
          )}
          <div className={styles.detailRow}>
            <span className={styles.label}>Posted</span>
            <span className={styles.value}>{formatDate(listing.created_at)}</span>
          </div>
        </div>
        
        <button 
          className={styles.reportButton} 
          onClick={() => setShowReportModal(true)}
        >
          Report this listing
        </button>

        <MessageBoard listing={listing} />
      </div>

      {showReportModal && (
        <div className={styles.modalOverlay} onClick={() => setShowReportModal(false)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <h2 className={styles.modalTitle}>Report Listing</h2>
            {reportSuccess ? (
              <p style={{ color: "#059669", fontWeight: "600" }}>Report submitted successfully!</p>
            ) : (
              <form onSubmit={handleReportSubmit}>
                {reportError && <p style={{ color: "#dc2626", marginBottom: "12px" }}>{reportError}</p>}
                <textarea
                  className={styles.modalTextarea}
                  placeholder="Why are you reporting this listing?"
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                  required
                />
                <div className={styles.modalActions}>
                  <button 
                    type="button" 
                    className={styles.modalCancelBtn}
                    onClick={() => setShowReportModal(false)}
                    disabled={isReporting}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    className={styles.modalSubmitBtn}
                    disabled={isReporting || !reportReason.trim()}
                  >
                    {isReporting ? "Submitting..." : "Submit Report"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
