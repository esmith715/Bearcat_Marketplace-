import { useEffect, useRef, useCallback } from "react";

let globalSocket = null;
const listeners = new Set();

function getSocket(token) {
  if (globalSocket && globalSocket.readyState === WebSocket.OPEN) {
    return globalSocket;
  }
  if (!token) return null;

  globalSocket = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

  globalSocket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      listeners.forEach((fn) => fn(data));
    } catch {
      // ignore malformed messages
    }
  };

  globalSocket.onclose = () => {
    globalSocket = null;
  };

  return globalSocket;
}

export function useWebSocket(onMessage) {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    getSocket(token);

    const handler = (data) => onMessageRef.current?.(data);
    listeners.add(handler);

    return () => {
      listeners.delete(handler);
    };
  }, []);

  const sendMessage = useCallback((payload) => {
    const token = localStorage.getItem("access_token");
    const socket = getSocket(token);
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload));
    }
  }, []);

  return { sendMessage };
}