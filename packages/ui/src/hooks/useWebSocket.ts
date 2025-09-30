import { useEffect, useRef, useState, useCallback } from 'react';

// DOM types for browser environment
type EventTargetType = {
  addEventListener(type: string, listener: (event: EventType) => void): void;
  removeEventListener(type: string, listener: (event: EventType) => void): void;
  dispatchEvent(event: EventType): boolean;
};

// DOM event types for browser environment
type EventType = {
  readonly type: string;
  readonly target: EventTargetType | null;
  readonly currentTarget: EventTargetType | null;
  preventDefault(): void;
  stopPropagation(): void;
};

type MessageEventType = EventType & {
  readonly data: string;
  readonly origin: string;
  readonly lastEventId: string;
};

type CloseEventType = EventType & {
  readonly code: number;
  readonly reason: string;
  readonly wasClean: boolean;
};

// WebSocket type for browser environment
type WebSocketType = {
  new (url: string): WebSocketType;
  readonly readyState: number;
  readonly OPEN: number;
  onopen: ((event: EventType) => void) | null;
  onmessage: ((event: MessageEventType) => void) | null;
  onclose: ((event: CloseEventType) => void) | null;
  onerror: ((event: EventType) => void) | null;
  close(): void;
};

declare const WebSocket: WebSocketType;

interface Recommendation {
  title: string;
  description: string;
  natural_language_query: string;
  category: string;
  priority: string;
  reasoning: string;
}

interface WebSocketMessage {
  type: string;
  user_id: string;
  recommendations?: Recommendation[];
  timestamp?: string;
}

interface UseWebSocketOptions {
  userId: string;
  onMessage?: (message: WebSocketMessage) => void;
  onRecommendationsReady?: (recommendations: Recommendation[]) => void;
}

export function useWebSocket({ userId, onMessage, onRecommendationsReady }: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const ws = useRef<WebSocketType | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const wsUrl = `ws://localhost:8000/ws/recommendations/${userId}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          if (message.type === 'recommendations_ready' && onRecommendationsReady && message.recommendations) {
            onRecommendationsReady(message.recommendations);
          }
          
          if (onMessage) {
            onMessage(message);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Attempt to reconnect with exponential backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000;
          reconnectAttempts.current++;
          
          reconnectTimeoutRef.current = window.setTimeout(() => {
            console.log(`Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts})...`);
            connect();
          }, delay);
        } else {
          setError('Failed to reconnect to server');
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
      };
    } catch (err) {
      console.error('Error creating WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [userId, onMessage, onRecommendationsReady]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    
    setIsConnected(false);
  }, []);

  useEffect(() => {
    if (userId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [userId, connect, disconnect]);

  return {
    isConnected,
    error,
    connect,
    disconnect,
  };
}
