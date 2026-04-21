import FavoriteListings from "../Profile/FavoriteListings";
import styles from "./Favorites.module.css";

export default function Favorites() {
  return (
    <div className={styles.page}>
      <h1 className={styles.heading}>My Favorites</h1>
      <FavoriteListings />
    </div>
  );
}