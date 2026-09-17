import React, { createContext, useContext, useEffect, useState } from "react";
import { beginOAuth, getUser, signOut as supabaseSignOut } from "../api/supabase";

const AuthContext = createContext(null);
const storageKey = "thethirdeye_session";
const storeSession = (session) => localStorage.setItem(storageKey, JSON.stringify(session));

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const restore = async () => {
      try {
        let saved = JSON.parse(localStorage.getItem(storageKey) || "null");
        
        // Handle OAuth callback hash
        const hash = window.location.hash;
        if (hash && hash.includes("access_token=")) {
          const params = new URLSearchParams(hash.substring(1));
          const access_token = params.get("access_token");
          const refresh_token = params.get("refresh_token");
          if (access_token) {
            saved = { access_token, refresh_token };
            storeSession(saved);
            window.location.hash = ""; // Clear hash for clean URL
          }
        }

        if (!saved?.access_token) return;
        const nextUser = await getUser(saved.access_token);
        setSession(saved);
        setUser(nextUser);
      } catch {
        localStorage.removeItem(storageKey);
      } finally {
        setIsLoading(false);
      }
    };
    restore();
  }, []);

  const signInWithOAuth = async (provider) => {
    try {
      beginOAuth(provider);
      return { data: null, error: null };
    } catch (error) {
      return { data: null, error };
    }
  };
  const signOut = async () => {
    setIsLoading(true);
    try {
      if (session?.access_token) await supabaseSignOut();
      return { error: null };
    } catch (error) {
      return { error };
    } finally {
      localStorage.removeItem(storageKey);
      setUser(null);
      setSession(null);
      setIsLoading(false);
    }
  };

  return <AuthContext.Provider value={{ user, session, isLoading, isAuthenticated: Boolean(user), signInWithOAuth, signOut, getSession: () => session }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
