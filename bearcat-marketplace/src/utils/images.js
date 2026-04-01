export function getImageSrc(imageUrl) {
  if (!imageUrl) return null;
  if (imageUrl.startsWith("http")) return imageUrl;
  return `http://localhost:8000${imageUrl}`;
}
