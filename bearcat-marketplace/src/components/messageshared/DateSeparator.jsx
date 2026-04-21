import styles from "./MessageShared.module.css";

/**
 * Props:
 *   date {string} — formatted date string, e.g. "Apr 19"
 */
export default function DateSeparator({ date }) {
  return (
    <div className={styles.dateSeparator}>
      <span>{date}</span>
    </div>
  );
}