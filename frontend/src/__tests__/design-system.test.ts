/**
 * Design System tests: design tokens validation
 */
import { describe, it, expect } from 'vitest';
import {
  typography,
  colors,
  semantic,
  chartColors,
  spacing,
  layout,
  shadow,
} from '@/styles/design-tokens';

// ---------------------------------------------------------------------------
// Typography tokens
// ---------------------------------------------------------------------------

describe('typography tokens', () => {
  it('has display font family defined', () => {
    expect(typography.family.display).toBeTruthy();
    expect(typography.family.display).toContain('serif');
  });

  it('has body font family defined', () => {
    expect(typography.family.body).toBeTruthy();
    expect(typography.family.body).toContain('sans-serif');
  });

  it('has mono font family defined', () => {
    expect(typography.family.mono).toBeTruthy();
    expect(typography.family.mono).toContain('monospace');
  });

  it('has xs size defined as 0.75rem', () => {
    expect(typography.size.xs).toBe('0.75rem');
  });

  it('has base size defined as 1rem', () => {
    expect(typography.size.base).toBe('1rem');
  });

  it('has normal and bold weights', () => {
    expect(typography.weight.normal).toBe('400');
    expect(typography.weight.bold).toBe('700');
  });
});

// ---------------------------------------------------------------------------
// Color tokens
// ---------------------------------------------------------------------------

describe('color tokens', () => {
  it('has a dark background color', () => {
    expect(colors.bg).toBeTruthy();
    expect(colors.bg).toMatch(/^#/);
  });

  it('amber color is defined as hex', () => {
    expect(colors.amber).toBe('#f0a020');
  });

  it('cyan color is defined as hex', () => {
    expect(colors.cyan).toBe('#00d4f5');
  });

  it('text color is defined', () => {
    expect(colors.text).toBe('#eceef8');
  });

  it('has surface variants', () => {
    expect(colors.surface).toBeTruthy();
    expect(colors.surface2).toBeTruthy();
    expect(colors.surface3).toBeTruthy();
  });

  it('has status colors', () => {
    expect(colors.success).toBeTruthy();
    expect(colors.error).toBeTruthy();
    expect(colors.info).toBeTruthy();
  });

  it('error color is red-like', () => {
    expect(colors.error).toBe('#ff5050');
  });

  it('success color is green-like', () => {
    expect(colors.success).toBe('#3dca74');
  });
});

// ---------------------------------------------------------------------------
// Semantic aliases
// ---------------------------------------------------------------------------

describe('semantic tokens', () => {
  it('primary maps to amber', () => {
    expect(semantic.primary).toBe(colors.amber);
  });

  it('secondary maps to cyan', () => {
    expect(semantic.secondary).toBe(colors.cyan);
  });

  it('error maps to colors.error', () => {
    expect(semantic.error).toBe(colors.error);
  });

  it('bgBase maps to colors.bg', () => {
    expect(semantic.bgBase).toBe(colors.bg);
  });

  it('text maps to colors.text', () => {
    expect(semantic.text).toBe(colors.text);
  });
});

// ---------------------------------------------------------------------------
// Chart colors
// ---------------------------------------------------------------------------

describe('chartColors', () => {
  it('primary chart color matches amber', () => {
    expect(chartColors.primary).toBe(colors.amber);
  });

  it('secondary chart color matches cyan', () => {
    expect(chartColors.secondary).toBe(colors.cyan);
  });

  it('has a series array', () => {
    expect(Array.isArray(chartColors.series)).toBe(true);
    expect(chartColors.series.length).toBeGreaterThan(0);
  });

  it('series contains amber as first color', () => {
    expect(chartColors.series[0]).toBe(colors.amber);
  });
});

// ---------------------------------------------------------------------------
// Spacing tokens
// ---------------------------------------------------------------------------

describe('spacing tokens', () => {
  it('has zero spacing', () => {
    expect(spacing[0]).toBe('0');
  });

  it('spacing 4 is 1rem', () => {
    expect(spacing[4]).toBe('1rem');
  });

  it('spacing 8 is 2rem', () => {
    expect(spacing[8]).toBe('2rem');
  });
});

// ---------------------------------------------------------------------------
// Layout tokens
// ---------------------------------------------------------------------------

describe('layout tokens', () => {
  it('sidebarCollapsed is 3.5rem (56px)', () => {
    expect(layout.sidebarCollapsed).toBe('3.5rem');
  });

  it('sidebarExpanded is 12.5rem (200px)', () => {
    expect(layout.sidebarExpanded).toBe('12.5rem');
  });

  it('topBarHeight is 3.5rem (56px)', () => {
    expect(layout.topBarHeight).toBe('3.5rem');
  });

  it('maxWidth is 80rem (1280px)', () => {
    expect(layout.maxWidth).toBe('80rem');
  });
});

// ---------------------------------------------------------------------------
// Shadow tokens
// ---------------------------------------------------------------------------

describe('shadow tokens', () => {
  it('amber shadow is defined', () => {
    expect(shadow.amber).toBeTruthy();
    expect(shadow.amber).toContain('rgba(240,160,32');
  });

  it('cyan shadow is defined', () => {
    expect(shadow.cyan).toBeTruthy();
  });

  it('gold shadow is defined', () => {
    expect(shadow.gold).toBeTruthy();
  });
});
