"use client";

import { toast } from "sonner";

export type ToastType = "success" | "error" | "warning" | "info";

export interface ToastOptions {
  duration?: number;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

/**
 * Hook for displaying toast notifications
 * Uses the Sonner toast library
 */
export function useToast() {
  return {
    success: (message: string, options?: ToastOptions) => {
      toast.success(message, options);
    },
    error: (message: string, options?: ToastOptions) => {
      toast.error(message, options);
    },
    warning: (message: string, options?: ToastOptions) => {
      toast.warning(message, options);
    },
    info: (message: string, options?: ToastOptions) => {
      toast.info(message, options);
    },
    loading: (message: string) => {
      return toast.loading(message);
    },
    dismiss: (toastId?: string | number) => {
      toast.dismiss(toastId);
    },
  };
}
