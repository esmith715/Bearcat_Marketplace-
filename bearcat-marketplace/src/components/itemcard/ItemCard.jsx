import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./ItemCard.module.css";
import { getImageSrc } from "../../utils/images";

export default function ItemCard({
  id,
  title,
  description,
  image,
  onClick,
  isFavorited = false,
  onToggleFavorite,
}) {
  const navigate = useNavigate();

  return (
    <div
      onClick={onClick}
      className={`${styles.card} ${onClick ? styles.clickable : ""}`}
    >
      <div className={styles.cardTop}>
        <button
          type="button"
          className={`${styles.favoriteButton} ${isFavorited ? styles.favorited : ""}`}
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite?.(id, isFavorited);
          }}
          aria-label={isFavorited ? "Remove favorite" : "Add favorite"}
          title={isFavorited ? "Remove favorite" : "Add favorite"}
        >
          ★
        </button>
      </div>

      {image && (
        <img
          src={getImageSrc(image)}
          alt={title}
          className={styles.image}
        />
      )}

      <h3 className={styles.title}>{title}</h3>
      <p className={styles.description}>{description}</p>

      <div className={styles.buttonContainer}>
        <button
          className={`${styles.button} ${styles.viewButton}`}
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/market/${id}`, {
              state: { from: "market" }
            });
          }}
        >
          View Details
        </button>

        <button
          className={`${styles.button} ${styles.buyButton}`}
          onClick={(e) => {
            e.stopPropagation();
            alert(`You want to buy ${title}`);
          }}
        >
          Buy
        </button>
      </div>
    </div>
  );
}
