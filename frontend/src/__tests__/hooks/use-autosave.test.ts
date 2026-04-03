/**
 * useAutosave hook tests
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAutosave } from '@/hooks/index';

describe('useAutosave', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns "idle" initially', () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    const { result } = renderHook(() =>
      useAutosave('data', { onSave, debounceMs: 1000 })
    );
    expect(result.current).toBe('idle');
  });

  it('does not call onSave before debounce delay', () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    renderHook(() => useAutosave('data', { onSave, debounceMs: 1000 }));
    vi.advanceTimersByTime(500);
    expect(onSave).not.toHaveBeenCalled();
  });

  it('calls onSave after debounce delay', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    renderHook(() => useAutosave('data', { onSave, debounceMs: 1000 }));
    await act(async () => {
      vi.advanceTimersByTime(1000);
    });
    expect(onSave).toHaveBeenCalledTimes(1);
  });

  it('passes current data to onSave', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    renderHook(() => useAutosave({ key: 'value' }, { onSave, debounceMs: 500 }));
    await act(async () => {
      vi.advanceTimersByTime(500);
    });
    expect(onSave).toHaveBeenCalledWith({ key: 'value' });
  });

  it('transitions to "saving" when timer fires', async () => {
    let resolvePromise!: () => void;
    const onSave = vi.fn().mockImplementation(
      () => new Promise<void>((r) => { resolvePromise = r; })
    );
    const { result } = renderHook(() =>
      useAutosave('data', { onSave, debounceMs: 100 })
    );
    await act(async () => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current).toBe('saving');
    await act(async () => { resolvePromise(); });
  });

  it('transitions to "saved" after successful save', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    const { result } = renderHook(() =>
      useAutosave('data', { onSave, debounceMs: 100 })
    );
    await act(async () => {
      vi.advanceTimersByTime(100);
      await Promise.resolve();
    });
    expect(result.current).toBe('saved');
  });

  it('transitions to "error" when onSave throws', async () => {
    const onSave = vi.fn().mockRejectedValue(new Error('Save failed'));
    const { result } = renderHook(() =>
      useAutosave('data', { onSave, debounceMs: 100 })
    );
    await act(async () => {
      vi.advanceTimersByTime(100);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(result.current).toBe('error');
  });

  it('resets to "idle" after 2s following saved', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    const { result } = renderHook(() =>
      useAutosave('data', { onSave, debounceMs: 100 })
    );
    await act(async () => {
      vi.advanceTimersByTime(100);
      await Promise.resolve();
    });
    expect(result.current).toBe('saved');
    await act(async () => {
      vi.advanceTimersByTime(2000);
    });
    expect(result.current).toBe('idle');
  });

  it('does not call onSave when enabled=false', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    renderHook(() =>
      useAutosave('data', { onSave, debounceMs: 100, enabled: false })
    );
    await act(async () => {
      vi.advanceTimersByTime(500);
    });
    expect(onSave).not.toHaveBeenCalled();
  });

  it('remains "idle" when enabled=false', () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    const { result } = renderHook(() =>
      useAutosave('data', { onSave, debounceMs: 100, enabled: false })
    );
    act(() => { vi.advanceTimersByTime(500); });
    expect(result.current).toBe('idle');
  });

  it('debounces repeated data changes', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    const { rerender } = renderHook(
      ({ data }: { data: string }) => useAutosave(data, { onSave, debounceMs: 500 }),
      { initialProps: { data: 'a' } }
    );
    act(() => { vi.advanceTimersByTime(300); });
    rerender({ data: 'ab' });
    act(() => { vi.advanceTimersByTime(300); });
    rerender({ data: 'abc' });
    await act(async () => {
      vi.advanceTimersByTime(500);
      await Promise.resolve();
    });
    // onSave should be called only once (after the final debounce settles)
    expect(onSave).toHaveBeenCalledTimes(1);
  });

  it('uses default debounce of 1500ms when not specified', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    renderHook(() => useAutosave('data', { onSave }));
    act(() => { vi.advanceTimersByTime(1400); });
    expect(onSave).not.toHaveBeenCalled();
    await act(async () => {
      vi.advanceTimersByTime(100);
      await Promise.resolve();
    });
    expect(onSave).toHaveBeenCalledTimes(1);
  });

  it('cancels pending save on unmount', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    const { unmount } = renderHook(() =>
      useAutosave('data', { onSave, debounceMs: 500 })
    );
    unmount();
    await act(async () => {
      vi.advanceTimersByTime(500);
      await Promise.resolve();
    });
    expect(onSave).not.toHaveBeenCalled();
  });
});
