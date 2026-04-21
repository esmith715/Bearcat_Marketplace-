// ─────────────────────────────────────────────────────────────────────────────
// messageUtils.js
//
// Shared pure utility functions for all messaging components.
// "Pure" means: given the same input, always returns the same output,
// and has no side effects (no API calls, no state changes, no DOM access).
// These are safe to import and use anywhere.
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Formats an ISO timestamp string into a human-readable time.
 * e.g. "2025-04-19T14:30:00Z" → "2:30 PM"
 */
export function formatTime(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

/**
 * Formats an ISO timestamp into a short date.
 * e.g. "2025-04-19T14:30:00Z" → "Apr 19"
 */
export function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

/**
 * For conversation list previews: shows time if today, date if older.
 * This is the same pattern used by iMessage, Gmail, Slack, etc.
 * e.g. a message from today → "2:30 PM"
 *      a message from last week → "Apr 12"
 */
export function formatPreviewTimestamp(iso) {
  if (!iso) return "";
  const msgDate = new Date(iso);
  const today = new Date();
  const isToday =
    msgDate.getFullYear() === today.getFullYear() &&
    msgDate.getMonth()    === today.getMonth()    &&
    msgDate.getDate()     === today.getDate();
  return isToday ? formatTime(iso) : formatDate(iso);
}

/**
 * Truncates a string to maxLen characters, appending "…" if cut.
 * Like Python's textwrap.shorten().
 */
export function truncate(str, maxLen = 55) {
  if (!str) return "";
  return str.length > maxLen ? str.slice(0, maxLen) + "…" : str;
}

/**
 * Groups a flat array of message objects into a mixed array of
 * date-separator entries and message entries, for rendering chat
 * history with "Apr 19" dividers between days.
 *
 * Input:  [{ created_at: "...", content: "hi" }, ...]
 * Output: [
 *   { type: "separator", date: "Apr 19" },
 *   { type: "message",   msg: { ... } },
 *   { type: "message",   msg: { ... } },
 *   { type: "separator", date: "Apr 20" },
 *   ...
 * ]
 */
export function groupByDate(msgs) {
  const groups = [];
  let lastDate = null;
  for (const msg of msgs) {
    const date = formatDate(msg.created_at);
    if (date !== lastDate) {
      groups.push({ type: "separator", date });
      lastDate = date;
    }
    groups.push({ type: "message", msg });
  }
  return groups;
}

/**
 * Decodes the JWT access token from localStorage to extract the
 * current user's ID (the "sub" claim).
 *
 * A JWT has three base64-encoded parts separated by ".":
 *   header.payload.signature
 * We only need the payload (index 1), which contains user info.
 *
 * Returns the user ID string, or null if decoding fails.
 * Failure is safe to ignore — it just means we can't determine
 * which bubbles to color as "mine".
 */
export function getCurrentUserId() {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) return null;
    // atob() decodes a base64 string — like Python's base64.b64decode()
    return JSON.parse(atob(token.split(".")[1])).sub ?? null;
  } catch {
    return null;
  }
}