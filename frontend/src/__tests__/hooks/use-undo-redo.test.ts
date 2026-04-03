/**
 * useUndoRedo hook tests
 */
import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useUndoRedo } from '@/hooks/index';

describe('useUndoRedo', () => {
  it('initial state is the passed value', () => {
    const { result } = renderHook(() => useUndoRedo('hello'));
    expect(result.current.state).toBe('hello');
  });

  it('initial state works with objects', () => {
    const initial = { count: 0 };
    const { result } = renderHook(() => useUndoRedo(initial));
    expect(result.current.state).toEqual({ count: 0 });
  });

  it('initial state works with arrays', () => {
    const { result } = renderHook(() => useUndoRedo([1, 2, 3]));
    expect(result.current.state).toEqual([1, 2, 3]);
  });

  it('canUndo is false initially', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    expect(result.current.canUndo).toBe(false);
  });

  it('canRedo is false initially', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    expect(result.current.canRedo).toBe(false);
  });

  it('push() changes state to new value', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    expect(result.current.state).toBe(1);
  });

  it('push() enables canUndo', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    expect(result.current.canUndo).toBe(true);
  });

  it('push() keeps canRedo false', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    expect(result.current.canRedo).toBe(false);
  });

  it('undo() reverts to previous state', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.undo(); });
    expect(result.current.state).toBe(0);
  });

  it('undo() enables canRedo', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.undo(); });
    expect(result.current.canRedo).toBe(true);
  });

  it('undo() disables canUndo when back to initial', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.undo(); });
    expect(result.current.canUndo).toBe(false);
  });

  it('redo() reapplies state', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.undo(); });
    act(() => { result.current.redo(); });
    expect(result.current.state).toBe(1);
  });

  it('canRedo is false after redo', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.undo(); });
    act(() => { result.current.redo(); });
    expect(result.current.canRedo).toBe(false);
  });

  it('canRedo is true after undo', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.undo(); });
    expect(result.current.canRedo).toBe(true);
  });

  it('undo() does nothing when canUndo is false', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));
    act(() => { result.current.undo(); });
    expect(result.current.state).toBe('initial');
  });

  it('redo() does nothing when canRedo is false', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));
    act(() => { result.current.redo(); });
    expect(result.current.state).toBe('initial');
  });

  it('multiple push() then undo back to beginning', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.push(2); });
    act(() => { result.current.push(3); });
    act(() => { result.current.undo(); });
    act(() => { result.current.undo(); });
    act(() => { result.current.undo(); });
    expect(result.current.state).toBe(0);
    expect(result.current.canUndo).toBe(false);
  });

  it('multiple pushes then full redo sequence', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.push(2); });
    act(() => { result.current.push(3); });
    act(() => { result.current.undo(); });
    act(() => { result.current.undo(); });
    act(() => { result.current.undo(); });
    act(() => { result.current.redo(); });
    act(() => { result.current.redo(); });
    act(() => { result.current.redo(); });
    expect(result.current.state).toBe(3);
    expect(result.current.canRedo).toBe(false);
  });

  it('push() clears redo history', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.undo(); });
    act(() => { result.current.push(2); });
    expect(result.current.canRedo).toBe(false);
    expect(result.current.state).toBe(2);
  });

  it('reset() clears history and sets new state', () => {
    const { result } = renderHook(() => useUndoRedo(0));
    act(() => { result.current.push(1); });
    act(() => { result.current.push(2); });
    act(() => { result.current.reset(99); });
    expect(result.current.state).toBe(99);
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(false);
  });

  it('maxHistory option limits past array', () => {
    const { result } = renderHook(() => useUndoRedo(0, { maxHistory: 3 }));
    act(() => { result.current.push(1); });
    act(() => { result.current.push(2); });
    act(() => { result.current.push(3); });
    act(() => { result.current.push(4); });
    act(() => { result.current.push(5); });
    // Can only undo 3 times (maxHistory=3)
    act(() => { result.current.undo(); });
    act(() => { result.current.undo(); });
    act(() => { result.current.undo(); });
    expect(result.current.canUndo).toBe(false);
  });

  it('works with string state', () => {
    const { result } = renderHook(() => useUndoRedo(''));
    act(() => { result.current.push('a'); });
    act(() => { result.current.push('ab'); });
    act(() => { result.current.undo(); });
    expect(result.current.state).toBe('a');
  });

  it('works with boolean state', () => {
    const { result } = renderHook(() => useUndoRedo(false));
    act(() => { result.current.push(true); });
    expect(result.current.state).toBe(true);
    act(() => { result.current.undo(); });
    expect(result.current.state).toBe(false);
  });
});
