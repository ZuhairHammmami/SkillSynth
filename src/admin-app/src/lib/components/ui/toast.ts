/** Toast store. Replaces sonner. */
import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'info';
export const toasts = writable<{ id: number; type: ToastType; message: string }[]>([]);

let counter = 0;

function push(type: ToastType, message: string) {
  const id = ++counter;
  toasts.update((list) => [...list, { id, type, message }]);
  setTimeout(() => toasts.update((list) => list.filter((t) => t.id !== id)), 4200);
}

export const success = (m: string) => push('success', m);
export const error = (m: string) => push('error', m);
export const info = (m: string) => push('info', m);
export const toast = push;
