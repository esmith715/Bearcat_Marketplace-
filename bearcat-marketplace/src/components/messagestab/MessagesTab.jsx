// ─────────────────────────────────────────────────────────────────────────────
// MessagesTab.jsx
//
// This component renders the full "Messages" section on the Home page.
// It has two parts:
//   1. A conversation list (like an inbox sidebar)
//   2. A message thread view (the actual chat for a selected conversation)
//
// ─────────────────────────────────────────────────────────────────────────────

import {
  formatDate,
  formatTime,
  formatPreviewTimestamp,
  truncate,
  groupByDate,
  getCurrentUserId,
} from "../../utils/messageUtils";
import MessageBubble from "../messageshared/MessageBubble";
import DateSeparator from "../messageshared/DateSeparator";
import { useWebSocket } from "../../hooks/useWebSocket";

import { useEffect, useRef, useState } from "react";

import { Link } from "react-router-dom";

import styles from "./MessagesTab.module.css";


// ─────────────────────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────────────────────────

export default function MessagesTab() {
  // ── STATE ────────────────────────────────────────────────────────────────
  const [conversations, setConversations] = useState([]);
  // List of conversation thread summaries fetched from /messages/conversations

  const [selectedConv, setSelectedConv] = useState(null);
  // The currently selected conversation object (or null if none selected)

  const [messages, setMessages] = useState([]);
  // The full message history for the selected conversation

  const [convLoading, setConvLoading] = useState(true);
  // True while fetching the conversation list

  const [msgLoading, setMsgLoading] = useState(false);
  // True while fetching the message thread for a selected conversation

  const [convError, setConvError] = useState(null);
  // Error string if fetching conversations fails, or null

  const [msgError, setMsgError] = useState(null);
  // Error string if fetching a message thread fails, or null

  const [input, setInput] = useState("");
  // What the user is currently typing in the reply box

  const [sending, setSending] = useState(false);
  // True while a message is being sent (prevents double-sends)

  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  const token = localStorage.getItem("access_token");

  // ── WEBSOCKET ────────────────────────────────────────────────────────────────
// One call does two things:
//   1. Gives us sendMessage to send outgoing messages
//   2. Registers a listener for incoming real-time messages
const { sendMessage } = useWebSocket((data) => {
  // Only handle direct messages
  if (data.type !== "direct_message") return;

  const msg = data.message;

  // Only add the message if it belongs to the currently open conversation.
  // Without this check, a message from a different conversation would
  // incorrectly appear in whatever thread is currently open.
  if (!selectedConv) return;
  if (msg.listing_id !== selectedConv.listing_id) return;

  const isRelevant =
    (msg.from_user_id === selectedConv.other_user_id) ||
    (msg.to_user_id === selectedConv.other_user_id);

  if (!isRelevant) return;

  // Deduplicate — if the real message arrived and replaced the optimistic one,
  // don't add it again. The replace logic in handleSend handles the swap.
  setMessages((prev) => {
    if (prev.find((m) => m.id === msg.id)) return prev;
    return [...prev, msg];
  });

  // Update the conversation preview in the left panel
  setConversations((prev) =>
    prev.map((c) =>
      c.listing_id === msg.listing_id &&
      (c.other_user_id === msg.from_user_id || c.other_user_id === msg.to_user_id)
        ? { ...c, content: msg.content, created_at: msg.created_at }
        : c
    )
  );
});

  // ── EFFECT: FETCH CONVERSATIONS ──────────────────────────────────────────
  useEffect(() => {
    // If the user isn't logged in, don't try to fetch anything.
    if (!token) {
      setConvLoading(false);
      return;
    }

    async function fetchConversations() {
      // We can't make useEffect itself async (React limitation),
      // so we define an async function inside it and call it immediately.
      setConvLoading(true);
      setConvError(null);
      try {
        const res = await fetch("http://localhost:8000/messages/conversations", {
          headers: {
            // Send the JWT token so the backend knows who we are.
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) throw new Error("Failed to load conversations");

        const data = await res.json();

        const sorted = Array.isArray(data)
          ? [...data].sort(
              (a, b) => new Date(b.created_at) - new Date(a.created_at)
            )
          : [];

        setConversations(sorted);
      } catch (err) {
        setConvError(err.message);
      } finally {
        setConvLoading(false);
      }
    }

    fetchConversations();
  }, []);

  // ── EFFECT: FETCH MESSAGE THREAD ─────────────────────────────────────────
  // This runs whenever `selectedConv` changes (i.e., user clicks a conversation).
  // The dependency array [selectedConv] tells React to re-run when it changes.
  useEffect(() => {
    if (!selectedConv || !token) return;

    async function fetchThread() {
      setMsgLoading(true);
      setMsgError(null);
      setMessages([]); // Clear old messages while loading new ones

      try {
        // Fetch the full message history for this conversation.
        const res = await fetch(
          `http://localhost:8000/messages/${selectedConv.listing_id}/${selectedConv.other_user_id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (!res.ok) throw new Error("Failed to load messages");
        const data = await res.json();

        setMessages(Array.isArray(data) ? [...data].reverse() : []);

        // Mark all messages in this conversation as read.
        // We fire-and-forget this (no await) — it's not critical if it fails.
        fetch(
          `http://localhost:8000/messages/${selectedConv.listing_id}/${selectedConv.other_user_id}/read-all`,
          { method: "PATCH", headers: { Authorization: `Bearer ${token}` } }
        ).catch(() => {});

        // Update the unread count to 0 in our local conversations list
        // so the badge disappears immediately without a full refetch.
        // .map() returns a new array (we never mutate state directly in React).
        setConversations((prev) =>
          prev.map((c) =>
            c.listing_id === selectedConv.listing_id &&
            c.other_user_id === selectedConv.other_user_id
              ? { ...c, unread_count: 0 } // spread copies all fields, then overrides unread_count
              : c
          )
        );
      } catch (err) {
        setMsgError(err.message);
      } finally {
        setMsgLoading(false);
      }
    }

    fetchThread();
  }, [selectedConv]); // Re-run whenever selectedConv changes

  // ── EFFECT: AUTO-SCROLL TO BOTTOM ────────────────────────────────────────
  // Whenever the messages array changes, scroll the chat to the bottom.
  // bottomRef.current is the actual DOM element — scrollIntoView() is a browser API.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── SEND HANDLER ─────────────────────────────────────────────────────────────
async function handleSend() {
  const content = input.trim();

  // Guard clauses — bail out if we shouldn't send
  if (!content || !selectedConv || sending) return;

  setSending(true);
  setInput("");

  // Decode the current user's ID from the JWT so the optimistic message
  // uses a real UUID instead of the sentinel "me" string.
  // This ensures isMine stays correct even after the optimistic message
  // is replaced by the real server response.
  let currentUserId = null;
  try {
    currentUserId = JSON.parse(atob(token.split(".")[1])).sub;
  } catch {
    // Leave as null — the message will still send, just won't be styled as "mine"
    // until the real message arrives back via WebSocket
  }

  // Optimistic update — show the message immediately before server confirms
  const optimistic = {
    id: `optimistic-${Date.now()}`,
    listing_id: selectedConv.listing_id,
    from_user_id: currentUserId ?? "me",  // real UUID if available, fallback to "me"
    to_user_id: selectedConv.other_user_id,
    content,
    is_read: false,
    created_at: new Date().toISOString(),
  };
  setMessages((prev) => [...prev, optimistic]);

  try {
    sendMessage({
      type: "direct_message",
      to: selectedConv.other_user_id,
      listing_id: selectedConv.listing_id,
      content,
    });

    // Note: we no longer await a response or replace the optimistic message here.
    // The real message will arrive back through the useWebSocket listener above,
    // which will add it to the list. The optimistic message will be deduplicated
    // and can be cleaned up — or left as-is since it looks identical to the user.

    // Update the conversation preview in the left panel immediately
    setConversations((prev) =>
      prev.map((c) =>
        c.listing_id === selectedConv.listing_id &&
        c.other_user_id === selectedConv.other_user_id
          ? { ...c, content, created_at: optimistic.created_at }
          : c
      )
    );
  } catch {
    // If sendMessage threw (e.g. socket not open), roll back the optimistic message
    setMessages((prev) => prev.filter((m) => m.id !== optimistic.id));
    setInput(content);
    setMsgError("Failed to send. Please check your connection and try again.");
  } finally {
    setSending(false);
    textareaRef.current?.focus();
  }
}

  // Handle Enter key to send (Shift+Enter = new line, just Enter = send)
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent the default newline from being inserted
      handleSend();
    }
  }

  // ── RENDER: NOT LOGGED IN ─────────────────────────────────────────────────
  if (!token) {
    return (
      <div className={styles.loginPrompt}>
        <span className={styles.loginIcon}>💬</span>
        <p className={styles.loginText}>
          <Link to="/login" className={styles.loginLink}>Log in</Link>{" "}
          to view your messages.
        </p>
      </div>
    );
  }

  // ── RENDER: MAIN UI ───────────────────────────────────────────────────────
  // Group the selected conversation's messages by date for display
  const grouped = groupByDate(messages);

  return (
    // The outer wrapper is a two-column flex container
    <div className={styles.panelWrapper}>

      {/* ── LEFT PANEL: CONVERSATION LIST ── */}
      <div className={styles.convList}>
        <div className={styles.convListHeader}>
          <h3 className={styles.convListTitle}>Conversations</h3>
        </div>

        {/* Loading state */}
        {convLoading && (
          <p className={styles.stateMsg}>Loading…</p>
        )}

        {/* Error state */}
        {!convLoading && convError && (
          <p className={styles.errorMsg}>{convError}</p>
        )}

        {/* Empty state */}
        {!convLoading && !convError && conversations.length === 0 && (
          <div className={styles.emptyConv}>
            <span className={styles.emptyIcon}>📭</span>
            <p>No messages yet.</p>
            <p className={styles.emptyHint}>
              Message a seller from any{" "}
              <Link to="/market" className={styles.inlineLink}>listing</Link>!
            </p>
          </div>
        )}

        {/* Conversation rows */}
        {!convLoading &&
          !convError &&
          conversations.map((conv) => {
            // Determine if this conversation row is currently selected
            const isSelected =
              selectedConv?.listing_id === conv.listing_id &&
              selectedConv?.other_user_id === conv.other_user_id;

            return (
              <button
                key={`${conv.listing_id}-${conv.other_user_id}`}
                className={`${styles.convRow} ${isSelected ? styles.convRowActive : ""}`}
                // Template literal with conditional class — applies the
                // "active" style only when this row is selected.
                onClick={() => setSelectedConv(conv)}
                aria-label={`Conversation with ${conv.other_username} about ${conv.listing_title}`}
              >
                {/* Avatar circle showing first letter of the other user's name */}
                <div className={styles.avatar}>
                  {conv.other_username?.[0]?.toUpperCase() ?? "?"}
                </div>

                <div className={styles.convMeta}>
                  <div className={styles.convTopRow}>
                    <span className={styles.convUsername}>
                      {conv.other_username}
                    </span>
                    <span className={styles.convTime}>
                      {formatPreviewTimestamp(conv.created_at)}
                    </span>
                  </div>
                  <div className={styles.convBottomRow}>
                    <span className={styles.convPreview}>
                      {/* Show the listing title + message preview */}
                      <span className={styles.convListing}>
                        {conv.listing_title}:
                      </span>{" "}
                      {truncate(conv.content)}
                    </span>
                    {/* Show unread badge only if there are unread messages */}
                    {conv.unread_count > 0 && (
                      <span className={styles.unreadBadge}>
                        {conv.unread_count}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
      </div>

      {/* ── RIGHT PANEL: MESSAGE THREAD ── */}
      <div className={styles.threadPanel}>
        {/* Placeholder when no conversation is selected */}
        {!selectedConv && (
          <div className={styles.noSelection}>
            <span className={styles.noSelectionIcon}>💬</span>
            <p>Select a conversation to view messages</p>
          </div>
        )}

        {/* Full thread view when a conversation is selected */}
        {selectedConv && (
          <>
            {/* Thread header */}
            <div className={styles.threadHeader}>
              <div className={styles.threadHeaderLeft}>
                <div className={styles.threadAvatar}>
                  {selectedConv.other_username?.[0]?.toUpperCase() ?? "?"}
                </div>
                <div>
                  <p className={styles.threadUsername}>
                    {selectedConv.other_username}
                  </p>
                  {/* Link to the actual listing page */}
                  <Link
                    to={`/market/${selectedConv.listing_id}`}
                    className={styles.threadListingLink}
                  >
                    {selectedConv.listing_title} →
                  </Link>
                </div>
              </div>
            </div>

            {/* Message list */}
            <div className={styles.messageList}>
              {msgLoading && (
                <p className={styles.stateMsg}>Loading messages…</p>
              )}
              {!msgLoading && msgError && (
                <p className={styles.errorMsg}>{msgError}</p>
              )}
              {!msgLoading && !msgError && messages.length === 0 && (
                <p className={styles.stateMsg}>No messages yet. Say hi! 👋</p>
              )}

              {/* Render grouped messages with date separators */}
                {(() => {
                    let currentUserId = null;
                try {
                    currentUserId = JSON.parse(atob(token.split(".")[1])).sub;
                } catch {
                    // Leave as null if decoding fails
                }

                return !msgLoading && grouped.map((item, i) => {
                    if (item.type === "separator") {
                    // FIX 2: Use the shared DateSeparator component
                    return <DateSeparator key={`sep-${i}`} date={item.date} />;
                    }

                    const msg = item.msg;

                    // from_user_id === "me" catches our optimistic messages
                    const isMine =
                    msg.from_user_id === "me" ||
                    msg.from_user_id === currentUserId;

                    return (
                    <MessageBubble
                        key={msg.id}
                        content={msg.content}
                        createdAt={msg.created_at}
                        isMine={isMine}
                    />
                    );
                });
                })()}

                {/* Invisible scroll target */}
                <div ref={bottomRef} />
            </div>

            {/* Reply input area */}
            <div className={styles.inputArea}>
              <textarea
                ref={textareaRef}
                className={styles.textarea}
                placeholder="Type a reply… (Enter to send, Shift+Enter for new line)"
                value={input}
                // "Controlled input" — React owns the value.
                // Every keystroke calls setInput, keeping `input` in sync with what's displayed.
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={2}
                disabled={sending}
              />
              <button
                className={styles.sendButton}
                onClick={handleSend}
                disabled={!input.trim() || sending}
                aria-label="Send message"
              >
                {/* Inline SVG "paper plane" icon — scales perfectly at any size */}
                <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                </svg>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}