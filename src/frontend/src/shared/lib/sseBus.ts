export type SseFrame = { type: string } & Record<string, unknown>;

type SseListener = (data: SseFrame) => void;

class SseBus {
  private listeners = new Map<string, Set<SseListener>>();

  on<T extends SseFrame = SseFrame>(
    type: string,
    listener: (data: T) => void
  ): () => void {
    const set = this.listeners.get(type) ?? new Set<SseListener>();
    set.add(listener as SseListener);
    this.listeners.set(type, set);
    return () => this.off(type, listener as SseListener);
  }

  off(type: string, listener: SseListener): void {
    this.listeners.get(type)?.delete(listener);
  }

  emit(type: string, data: SseFrame): void {
    const set = this.listeners.get(type);
    if (!set) return;
    for (const listener of [...set]) {
      try {
        listener(data);
      } catch {
        /* listener errors must not break the stream */
      }
    }
  }
}

export const sseBus = new SseBus();
