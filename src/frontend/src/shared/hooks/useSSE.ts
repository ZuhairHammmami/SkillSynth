'use client';

import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient, type QueryKey } from '@tanstack/react-query';
import { toast } from 'sonner';
import Cookies from 'js-cookie';
import { queryKeys } from '@/shared/api/query-keys';

interface SSEEvent {
  type: string;
  [key: string]: unknown;
}

type EventHandler = (event: SSEEvent) => void;

interface EventMap {
  [eventType: string]: EventHandler;
}

const DEFAULT_HANDLERS: EventMap = {
  progress_update: () => {},
  notification: (event) => {
    const title = event.title as string;
    const message = event.message as string;
    const type = (event.type as string) || 'info';
    const notifType = event.notification_type as string || type;
    if (notifType === 'success' || notifType === 'achievement') {
      toast.success(title, { description: message, duration: 4000 });
    } else if (notifType === 'warning' || notifType === 'error') {
      toast.error(title, { description: message, duration: 5000 });
    } else {
      toast.info(title, { description: message, duration: 3000 });
    }
  },
  system_alert: (event) => {
    const level = event.level as string;
    const message = event.message as string;
    if (level === 'error' || level === 'critical') {
      toast.error(message, { duration: 6000 });
    } else if (level === 'warning') {
      toast.warning(message, { duration: 5000 });
    } else {
      toast.info(message, { duration: 4000 });
    }
  },
  path_completed: (event) => {
    const title = event.path_title as string;
    toast.success('Path Completed!', {
      description: `You completed "${title}"`,
      duration: 5000,
    });
  },
  assessment_result: (event) => {
    const passed = event.passed as boolean;
    const percentage = event.percentage as number;
    if (passed) {
      toast.success('Assessment Passed!', {
        description: `Score: ${percentage}%`,
        duration: 4000,
      });
    } else {
      toast.warning('Assessment Needs Review', {
        description: `Score: ${percentage}%`,
        duration: 5000,
      });
    }
  },
  admin_alert: (event) => {
    const level = event.level as string;
    const message = event.message as string;
    if (level === 'critical') {
      toast.error(`Admin Alert: ${message}`, { duration: 8000 });
    } else {
      toast.warning(`Admin: ${message}`, { duration: 5000 });
    }
  },
  connected: () => {},
  ping: () => {},
};

function buildQueryInvalidations(eventType: string): readonly QueryKey[] {
  switch (eventType) {
    case 'progress_update':
    case 'step_completed':
      return [queryKeys.paths.all, queryKeys.compat.pathAll(), queryKeys.compat.dashboard()];
    case 'step_reverted':
      return [queryKeys.compat.pathAll(), queryKeys.compat.dashboard()];
    case 'analytics_refresh':
      return [
        queryKeys.compat.analyticsDashboard(),
        queryKeys.analytics.all,
        queryKeys.compat.skillGrowth(),
      ];
    case 'path_completed':
    case 'path_generated':
      return [queryKeys.paths.all, queryKeys.compat.dashboard()];
    case 'assessment_result':
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
