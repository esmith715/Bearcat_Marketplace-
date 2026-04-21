import { formatTime, formatDate, groupByDate, getCurrentUserId } from "../../utils/messageUtils";
import MessageBubble from "../messageshared/MessageBubble";
import DateSeparator from "../messageshared/DateSeparator";

import { useEffect, useRef, useState } from "react";

import { useWebSocket } from "../../hooks/useWebSocket";

import { useAuth } from "../../hooks/useAuth";

import styles from "./MessageBoard.module.css";

export default function MessageBoard({ listing }) {

  const { currentUser } = useAuth();

  const [messages, setMessages] = useState([]);

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(true);

  const [sending, setSending] = useState(false);

  const [error, setError] = useState(null);

  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  const token = localStorage.getItem("access_token");

  const isSeller = currentUser?.id === listing?.created_by;

  const otherUserId = isSeller ? null : listing?.created_by;

  useEffect(() => {
    // If we don't have a token, listing ID, or a seller to message, stop here.
    // This handles the "not logged in" and "seller viewing own listing" cases.
    if (!token || !listing?.id || !otherUserId) {
      setLoading(false); // Stop showing the loading spinner
      return;
    }

    async function fetchHistory() {
      setLoading(true); // Show loading spinner
      try {
        const res = await fetch(
          `http://localhost:8000/messages/${listing.id}/${otherUserId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!res.ok) throw new Error("Failed to load messages");

        const data = await res.json();

        setMessages(Array.isArray(data) ? [...data].reverse() : []);

      } catch (err) {
        // err.message is the error string — store it to display to the user.
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchHistory(); // Call the async function we just defined
  }, [listing?.id, otherUserId, token]);
  // ↑ Re-run this effect if any of these values change.

  // ── EFFECT: MARK CONVERSATION AS READ ──────────────────────────────────────
  // When the user opens the message board, mark all messages as read.
  useEffect(() => {
    if (!token || !listing?.id || !otherUserId) return;

    fetch(`http://localhost:8000/messages/${listing.id}/${otherUserId}/read-all`, {
      method: "PATCH", // HTTP PATCH — partial update (like your backend's @router.patch)
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => {}); // Silently ignore errors — not critical if this fails
  }, [listing?.id, otherUserId, token]);

  // ── EFFECT: AUTO-SCROLL TO BOTTOM ──────────────────────────────────────────
  // Whenever the messages array changes (new message added), scroll to the bottom.
  // bottomRef.current is the actual DOM element — calling .scrollIntoView()
  // on it tells the browser to scroll it into view.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    // behavior: "smooth" gives a nice animated scroll instead of jumping.
  }, [messages]); // Re-run whenever `messages` changes

  // ── WEBSOCKET: REAL-TIME INCOMING MESSAGES ─────────────────────────────────
  // useWebSocket calls our callback function whenever a WebSocket message arrives.
  // This is how we receive messages in real-time without refreshing the page.
  useWebSocket((data) => {
    // `data` is the parsed JSON object from the WebSocket.

    // Only handle direct_message events for THIS listing
    if (
      data.type === "direct_message" &&
      data.message?.listing_id === listing?.id
    ) {
      const msg = data.message;

      // Only show messages that are part of OUR conversation.
      // A message is relevant if it's between us and the other user.
      const isRelevant =
        (msg.from_user_id === otherUserId && msg.to_user_id === currentUser?.id) ||
        (msg.from_user_id === currentUser?.id && msg.to_user_id === otherUserId);

      if (isRelevant) {
        // Update the messages array by adding the new message.
        // We use the "functional update" form of setState:
        //   setMessages(prev => newValue)
        // This is safer than setMessages([...messages, msg]) because it
        // always uses the LATEST value of messages, avoiding stale state bugs.
        setMessages((prev) => {
          // Avoid duplicates — our optimistic update already added the message
          // if WE sent it. The server's echo would add it again without this check.
          if (prev.find((m) => m.id === msg.id)) return prev;
          return [...prev, msg]; // Spread existing messages + append new one
        });
      }
    }
  });

  // Get the sendMessage function from our WebSocket hook.
  // We call this separately (second call to useWebSocket) to get the sender.
  const { sendMessage } = useWebSocket();

  // ── SEND MESSAGE HANDLER ───────────────────────────────────────────────────
  // This function runs when the user clicks Send or presses Enter.
  // It's `async` because... well, actually we don't await anything critical here,
  // but it's good practice when the function might do async work.
  async function handleSend() {
    const content = input.trim(); // .trim() removes leading/trailing whitespace
    // Guard clauses — don't send if: empty message, no recipient, or already sending
    if (!content || !otherUserId || sending) return;

    setSending(true); // Disable the send button to prevent double-sends
    setInput("");      // Clear the text input immediately (good UX)

    // ── OPTIMISTIC UPDATE ──────────────────────────────────────────────────
    // "Optimistic update" means: show the message in the UI immediately,
    // BEFORE the server confirms it was saved. This makes the app feel fast.
    // If sending fails, we remove it (see the catch block below).
    //
    // We create a temporary message object with a fake ID.
    // The real message (with a real UUID from the database) will arrive
    // back via WebSocket, and our duplicate-check above will handle that.
    const optimistic = {
      id: `optimistic-${Date.now()}`, // Temporary unique ID using timestamp
      listing_id: listing.id,
      from_user_id: currentUser.id,   // We are the sender
      to_user_id: otherUserId,        // Seller is the recipient
      content,
      is_read: false,
      created_at: new Date().toISOString(), // Current time in ISO format
    };
    // Add the optimistic message to the list
    setMessages((prev) => [...prev, optimistic]);

    try {
      // Send the message via WebSocket.
      sendMessage({
        type: "direct_message",
        to: otherUserId,
        listing_id: listing.id,
        content, 
      });
    } catch {
      // If sending failed, show an error and remove the optimistic message
      setError("Failed to send message. Please try again.");
      setMessages((prev) => prev.filter((m) => m.id !== optimistic.id));
      // .filter() returns a new array excluding the failed message
      setInput(content); // Restore what they typed so they can try again
    } finally {
      setSending(false); // Re-enable the send button
      // Focus the textarea so the user can keep typing without clicking
      textareaRef.current?.focus();
    }
  }

  // ── KEYBOARD HANDLER ───────────────────────────────────────────────────────
  // Handle Enter key to send, Shift+Enter for a new line (standard chat behavior).
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Stop the default behavior (which would add a newline)
      handleSend();
    }
    // If Shift+Enter: e.shiftKey is true, so we skip this block → newline is added normally
  }

  // ── EARLY RETURNS (CONDITIONAL RENDERING) ─────────────────────────────────
  // Case 1: User is not logged in
  if (!token) {
    return (
      <div className={styles.loginPrompt}>
        <span>💬</span>
        <p>
          <a href="/login" className={styles.loginLink}>Log in</a> to message the seller.
        </p>
      </div>
    );
  }

  // Case 2: The current user is the seller (viewing their own listing)
  if (isSeller) {
    return (
      <div className={styles.sellerNote}>
        <span>📋</span>
        <p>This is your listing. Buyers will be able to message you here.</p>
      </div>
    );
  }

  // ── MAIN RENDER ────────────────────────────────────────────────────────────
  // Group messages for display (adds date separators)
  const grouped = groupByDate(messages);

  return (
    <div className={styles.board}>

      {/* ── HEADER ── */}
      <div className={styles.boardHeader}>
        <h3 className={styles.boardTitle}>💬 Message Seller</h3>
        <span className={styles.boardSub}>
          Messages are private between you and the seller
        </span>
      </div>

      {/* ── MESSAGE LIST ── */}
      <div className={styles.messageList}>
        {loading && <div className={styles.loadingMsg}>Loading messages...</div>}

        {/* Show error if one occurred */}
        {!loading && error && <div className={styles.errorMsg}>{error}</div>}

        {/* Show empty state if no messages and no error */}
        {!loading && !error && messages.length === 0 && (
          <div className={styles.emptyMsg}>
            No messages yet. Say hi! 👋
          </div>
        )}

        {/* Render the grouped messages (with date separators) */}
        {!loading &&
          grouped.map((item, i) => {
          if (item.type === "separator") {
            // DateSeparator is the shared component — same visual output,
            // but now defined in one place for both MessageBoard and MessagesTab.
            return <DateSeparator key={`sep-${i}`} date={item.date} />;
          }

            const msg = item.msg;
            const isMine = msg.from_user_id === currentUser?.id;

            return (
            // MessageBubble handles the left/right alignment and color automatically.
            // We pass isMine so it knows which style to apply.
            // Note: the read receipt (✓✓) is MessageBoard-specific, so we keep
            // it here as a child rather than baking it into the shared component.
            <MessageBubble
                key={msg.id}
                content={msg.content}
                createdAt={msg.created_at}
                isMine={isMine}
                readReceipt={isMine ? (msg.is_read ? " ✓✓" : " ✓") : null}
            />
            );
        })}

        {/* This invisible div at the bottom is our scroll target.
            The ref={bottomRef} connects it to our bottomRef variable above.
            When we call bottomRef.current.scrollIntoView(), the browser
            scrolls to this element — effectively scrolling to the bottom. */}
        <div ref={bottomRef} />
      </div>

      {/* ── INPUT AREA ── */}
      <div className={styles.inputArea}>
        <textarea
          ref={textareaRef}        // Connect to our ref so we can focus it programmatically
          className={styles.textarea}
          placeholder="Type a message… (Enter to send, Shift+Enter for new line)"
          value={input}            // "Controlled input" — React controls the value
          onChange={(e) => setInput(e.target.value)}
          // onChange fires on every keystroke. e.target.value is the current text.
          // This is "controlled component" pattern — the input's value is always
          // in sync with our `input` state variable. React owns the value.
          onKeyDown={handleKeyDown} // Call our keyboard handler on key press
          rows={2}                 // Initial height of the textarea (2 lines)
          disabled={sending}       // Disable while sending to prevent edits mid-send
        />

        <button
          className={styles.sendButton}
          onClick={handleSend}
          // Disable the button if: input is empty (after trimming) OR currently sending
          disabled={!input.trim() || sending}
          aria-label="Send message"
          // aria-label is an accessibility attribute — screen readers will announce
          // "Send message" for this button. Good practice for icon-only buttons!
        >
          {/* Show a spinner while sending, otherwise show the send icon */}
          {sending ? (
            <span className={styles.spinner} />
          ) : (
            // Inline SVG icon — this is a "paper plane" send icon.
            // SVGs are vector graphics defined in XML/HTML — they scale perfectly.
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}