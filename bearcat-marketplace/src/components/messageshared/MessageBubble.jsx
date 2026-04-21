import styles from "./MessageShared.module.css";
import { formatTime } from "../../utils/messageUtils";

/**
 * Props:
 *   content   {string}  — the message text
 *   createdAt {string}  — ISO timestamp string
 *   isMine    {boolean} — true if sent by the current user
 */
export default function MessageBubble({ content, createdAt, isMine, readReceipt = null }) {
  return (
    // The row aligns the bubble left or right depending on isMine.
    // Template literal applies a second class conditionally —
    // same pattern used throughout the rest of the codebase.
    <div className={`${styles.msgRow} ${isMine ? styles.msgRowMine : styles.msgRowTheirs}`}>
      <div className={`${styles.bubble} ${isMine ? styles.bubbleMine : styles.bubbleTheirs}`}>
        <span className={styles.bubbleText}>{content}</span>
        <span className={styles.bubbleTime}>
          {formatTime(createdAt)}
          {readReceipt && <span className={styles.readStatus}>{readReceipt}</span>}
        </span>
      </div>
    </div>
  );
}