'use client';

import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient, type QueryKey } from '@tanstack/react-query';
import Cookies from 'js-cookie';
import { queryKeys } from '@/shared/api/query-keys';
import { sseBus } from '@/shared/lib/sseBus';

interface SSEEvent {
  type: string;
  [key: string]: unknown;
}

type EventHandler = (event: SSEEvent) => void;

interface EventMap {
  [eventType: string]: EventHandler;
}

// Only event types the backend actually emits (events/publisher.py +
// send_event call sites): connected, ping, path_generated, assessment_completed.
const DEFAULT_HANDLERS: EventMap = {
  connected: () => {},
  ping: () => {},
};

function buildQueryInvalidations(eventType: string): readonly QueryKey[] {
  switch (eventType) {
    case 'path_generated':
      return [queryKeys.paths.all, queryKeys.compat.dashboard()];
    case 'assessment_completed':
      return [queryKeys.assessments.all, queryKeys.compat.analyticsDashboard()];
    default:
      return [];
  }
}

export function useSSE(enabled: boolean = true, isAdmin: boolean = false) {
  const queryClient = useQueryClient();
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!enabled || !mountedRef.current) return;

    const token = Cookies.get('authToken');
    if (!token) return;

    const endpoint = isAdmin
      ? `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'}/realtime/admin/events?token=${encodeURIComponent(token)}`
      : `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'}/realtime/events?token=${encodeURIComponent(token)}`;

    const es = new EventSource(endpoint);
    eventSourceRef.current = es;

    es.onopen = () => {};

    es.addEventListener('message', (event) => {
      try {
        const data: SSEEvent = JSON.parse(event.data);

        if (data.type !== 'connected' && data.type !== 'ping') {
          sseBus.emit(data.type, data);
        }

        const handlers = DEFAULT_HANDLERS;

        if (handlers[data.type]) {
          handlers[data.type](data);
        }

        const invalidations = buildQueryInvalidations(data.type);
        for (const key of invalidations) {
          queryClient.invalidateQueries({ queryKey: key });
        }
      } catch {
        /* ignore parse errors */
      }
    });

    es.addEventListener('connected', () => {});

    es.addEventListener('ping', () => {});

    es.onerror = () => {
      es.close();
      eventSourceRef.current = null;
      if (mountedRef.current) {
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      }
    };
  }, [enabled, isAdmin, queryClient]);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [connect]);

  return { isConnected: !!eventSourceRef.current };
}
