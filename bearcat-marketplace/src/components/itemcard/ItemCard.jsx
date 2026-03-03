import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./ItemCard.module.css";

export default function ItemCard({
  id,
  title,
  description,
  image,
  onClick,
}) {
  
  const navigate = useNavigate();

  return (
    <div
      onClick={onClick}
      className={`${styles.card} ${onClick ? styles.clickable : ""}`}
    >
      {image && (
        <img
          src={image}
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
            navigate(`/market/${id}`);
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
