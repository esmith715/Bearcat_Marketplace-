import ListingForm from "../listingform/ListingForm";
import styles from "./EditListingModal.module.css";

export default function EditListingModal({ listing, onClose, onUpdated }) {
  async function handleUpdate(payload, imageFile) {
    const token = localStorage.getItem("access_token");

    const res = await fetch(`http://localhost:8000/listings/${listing.id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Failed to update listing");
    }

    let updated = await res.json();

    if (imageFile) {
      const formData = new FormData();
      formData.append("image", imageFile);

      const uploadRes = await fetch(`http://localhost:8000/listings/${listing.id}/image`, {
        method: "POST",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: formData,
      });

      if (!uploadRes.ok) {
        const data = await uploadRes.json();
        throw new Error(data.detail || "Failed to upload image");
      }

      updated = await uploadRes.json();
    }

    onUpdated(updated);
    onClose();
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Edit Listing</h2>
          <button className={styles.closeButton} onClick={onClose}>
            ✕
          </button>
        </div>

        <ListingForm
          initialData={listing}
          onSubmit={handleUpdate}
          onCancel={onClose}
          submitText="Save Changes"
          submittingText="Saving..."
        />
      </div>
    </div>
  );
}
