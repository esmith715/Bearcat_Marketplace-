import { useState, useEffect } from "react";

function parseJwt(token) {
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

export function useAuth() {
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    const payload = parseJwt(token);
    if (payload) {
      // Your JWT payload contains `id` based on the backend token structure
      setCurrentUser({ id: payload.sub, ...payload });
    }
  }, []);

  return { currentUser };
}