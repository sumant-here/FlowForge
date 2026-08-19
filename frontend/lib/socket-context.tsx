"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

interface TelemetryEvent {
  event: string;
  data: any;
  timestamp: number;
}

interface SocketContextType {
  isConnected: boolean;
  lastEvent: TelemetryEvent | null;
  eventsHistory: TelemetryEvent[];
}

const SocketContext = createContext<SocketContextType>({
  isConnected: false,
  lastEvent: null,
  eventsHistory: [],
});

export function SocketProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<TelemetryEvent | null>(null);
  const [eventsHistory, setEventsHistory] = useState<TelemetryEvent[]>([]);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connect = () => {
      try {
        const wsUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000")
          .replace("http://", "ws://")
          .replace("https://", "wss://");

        ws = new WebSocket(`${wsUrl}/api/v1/ws`);

        ws.onopen = () => {
          setIsConnected(true);
        };

        ws.onmessage = (e) => {
          try {
            const parsed = JSON.parse(e.data);
            setLastEvent(parsed);
            setEventsHistory((prev) => [parsed, ...prev.slice(0, 49)]);
          } catch (err) {}
        };

        ws.onclose = () => {
          setIsConnected(false);
          reconnectTimeout = setTimeout(connect, 3000);
        };

        ws.onerror = () => {
          ws?.close();
        };
      } catch (e) {
        setIsConnected(false);
        reconnectTimeout = setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  return (
    <SocketContext.Provider value={{ isConnected, lastEvent, eventsHistory }}>
      {children}
    </SocketContext.Provider>
  );
}

export const useSocket = () => useContext(SocketContext);
