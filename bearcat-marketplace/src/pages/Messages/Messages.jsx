import MessagesTab from "../../components/messagestab/MessagesTab";
import styles from "./Messages.module.css";

export default function Messages() {
  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <h1 className={styles.title}>Messages</h1>
        {/* MessagesTab is self-contained — it fetches its own data */}
        <MessagesTab />
      </div>
    </div>
  );
}