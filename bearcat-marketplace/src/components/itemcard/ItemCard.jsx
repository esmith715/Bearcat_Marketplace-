import React from "react";
import { useNavigate } from "react-router-dom";

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
      style={{
        border: "1px solid #ddd",
        borderRadius: "10px",
        padding: "16px",
        width: "260px",
        cursor: onClick ? "pointer" : "default",
        boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
        transition: "0.2s",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {image && (
        <img
          src={image}
          alt={title}
          style={{
            width: "100%",
            height: "150px",
            objectFit: "cover",
            borderRadius: "8px",
            marginBottom: "12px",
          }}
        />
      )}

      <h3 style={{ margin: "0 0 8px" }}>{title}</h3>
      <p style={{ color: "#555", margin: "0 0 12px" }}>{description}</p>

      <div style={{ marginTop: "auto", display: "flex", gap: "10px" }}>
        <button
          style={{
            padding: "8px 16px",
            backgroundColor: "#007bff",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/market/${id}`);
          }}
        >
          View Details
        </button>

        <button
          style={{
            padding: "8px 16px",
            backgroundColor: "#dc3545",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
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
