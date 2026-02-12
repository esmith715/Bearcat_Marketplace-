import React from "react";

export default function ItemCard({
  title,
  description,
  image,
  onClick,
  footer,
}) {
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
      <p style={{ color: "#555", marginBottom: "12px" }}>{description}</p>

      {footer && <div>{footer}</div>}
    </div>
  );
}
