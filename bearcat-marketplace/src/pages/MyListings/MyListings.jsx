import UserListings from "../Profile/UserListings";
import styles from "./MyListings.module.css";

export default function MyListings() {
  return (
    <div className={styles.page}>
      <h1 className={styles.heading}>My Listings</h1>
      <UserListings />
    </div>
  );
}