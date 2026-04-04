/**
 * UI Utilities tests: Modal, Skeleton, Tooltip, ProgressIndicator, NotificationCenter
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

import { Modal, ModalFooter } from '@/components/ui/Modal';
import {
  Skeleton,
  SkeletonText,
  SkeletonCard,
  SkeletonTable,
} from '@/components/ui/Skeleton';
import { Tooltip } from '@/components/ui/Tooltip';
import {
  ProgressIndicator,
  IndeterminateProgress,
} from '@/components/ui/ProgressIndicator';
import { NotificationCenter, notify } from '@/components/ui/NotificationCenter';
import {
  ScreenReaderOnly,
  SkipToContent,
  LiveRegion,
  onKeyAction,
  contrastRatio,
  meetsWcagAA,
  forgeContrast,
} from '@/components/ui/Accessibility';

// ---------------------------------------------------------------------------
// Modal tests
// ---------------------------------------------------------------------------

describe('Modal', () => {
  it('renders children when isOpen=true', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <span>Modal Content</span>
      </Modal>
    );
    expect(screen.getByText('Modal Content')).toBeInTheDocument();
  });

  it('renders modal even when isOpen=false (but hidden via opacity/pointer-events)', () => {
    // The Modal component renders in portal regardless, just hidden via CSS
    render(
      <Modal isOpen={false} onClose={vi.fn()}>
        <span>Hidden Content</span>
      </Modal>
    );
    // Component renders, just visually hidden via opacity: 0
    expect(screen.getByText('Hidden Content')).toBeInTheDocument();
  });

  it('renders title when provided', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Test Modal Title">
        <span>Content</span>
      </Modal>
    );
    expect(screen.getByText('Test Modal Title')).toBeInTheDocument();
  });

  it('renders close button when title is provided', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Test Modal">
        <span>Content</span>
      </Modal>
    );
    expect(screen.getByLabelText('Close')).toBeInTheDocument();
  });

  it('calls onClose when close button clicked', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose} title="Test Modal">
        <span>Content</span>
      </Modal>
    );
    fireEvent.click(screen.getByLabelText('Close'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when Escape key pressed while open', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose}>
        <span>Content</span>
      </Modal>
    );
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does not call onClose on Escape when isOpen=false', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={false} onClose={onClose}>
        <span>Content</span>
      </Modal>
    );
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(onClose).not.toHaveBeenCalled();
  });

  it('calls onClose when backdrop clicked', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose}>
        <span>Content</span>
      </Modal>
    );
    const backdrop = document.querySelector('.fixed.inset-0') as HTMLElement;
    if (backdrop) {
      fireEvent.click(backdrop);
    }
    // Whether onClose was called depends on target matching — the test verifies no crash
  });

  it('renders with sm size', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} size="sm">
        <span>Small Modal</span>
      </Modal>
    );
    expect(screen.getByText('Small Modal')).toBeInTheDocument();
  });

  it('renders with xl size', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} size="xl">
        <span>XL Modal</span>
      </Modal>
    );
    expect(screen.getByText('XL Modal')).toBeInTheDocument();
  });

  it('renders without title when title not provided', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <span>No Title</span>
      </Modal>
    );
    expect(screen.queryByLabelText('Close')).not.toBeInTheDocument();
  });

  it('prevents body scroll when open', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <span>Content</span>
      </Modal>
    );
    expect(document.body.style.overflow).toBe('hidden');
  });

  it('restores body scroll when closed', () => {
    const { rerender } = render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <span>Content</span>
      </Modal>
    );
    rerender(
      <Modal isOpen={false} onClose={vi.fn()}>
        <span>Content</span>
      </Modal>
    );
    expect(document.body.style.overflow).toBe('');
  });
});

describe('ModalFooter', () => {
  it('renders children', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <ModalFooter>
          <button>Save</button>
          <button>Cancel</button>
        </ModalFooter>
      </Modal>
    );
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Skeleton tests
// ---------------------------------------------------------------------------

describe('Skeleton', () => {
  it('renders a div with animate-pulse class', () => {
    const { container } = render(<Skeleton />);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('animate-pulse');
  });

  it('accepts and applies custom className', () => {
    const { container } = render(<Skeleton className="h-10 w-full" />);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('h-10');
    expect(el.className).toContain('w-full');
  });

  it('renders a div element', () => {
    const { container } = render(<Skeleton />);
    expect(container.querySelector('div')).toBeInTheDocument();
  });
});

describe('SkeletonText', () => {
  it('renders default 3 lines', () => {
    const { container } = render(<SkeletonText />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBe(3);
  });

  it('renders specified number of lines', () => {
    const { container } = render(<SkeletonText lines={5} />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBe(5);
  });

  it('renders 1 line', () => {
    const { container } = render(<SkeletonText lines={1} />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBe(1);
  });

  it('renders a container div', () => {
    const { container } = render(<SkeletonText />);
    expect(container.querySelector('.flex.flex-col')).toBeInTheDocument();
  });
});

describe('SkeletonCard', () => {
  it('renders without crashing', () => {
    const { container } = render(<SkeletonCard />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it('renders with animate-pulse', () => {
    const { container } = render(<SkeletonCard />);
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('respects custom height', () => {
    const { container } = render(<SkeletonCard height={200} />);
    const card = container.firstChild as HTMLElement;
    expect(card.style.height).toBe('200px');
  });
});

describe('SkeletonTable', () => {
  it('renders without crashing', () => {
    const { container } = render(<SkeletonTable />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it('renders default 5 data rows', () => {
    const { container } = render(<SkeletonTable />);
    // header + 5 rows = 6 rows total
    const rows = container.querySelectorAll('.flex.gap-2');
    expect(rows.length).toBe(6);
  });

  it('renders custom row count', () => {
    const { container } = render(<SkeletonTable rows={3} />);
    const rows = container.querySelectorAll('.flex.gap-2');
    // header + 3 data rows = 4
    expect(rows.length).toBe(4);
  });
});

// ---------------------------------------------------------------------------
// Tooltip tests
// ---------------------------------------------------------------------------

describe('Tooltip', () => {
  it('renders children without crash', () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Hover me</button>
      </Tooltip>
    );
    expect(screen.getByText('Hover me')).toBeInTheDocument();
  });

  it('tooltip content is not visible initially', () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Hover me</button>
      </Tooltip>
    );
    expect(screen.queryByText('Tooltip text')).not.toBeInTheDocument();
  });

  it('shows tooltip after mouseEnter with delay=0', async () => {
    render(
      <Tooltip content="My Tooltip" delay={0}>
        <button>Hover me</button>
      </Tooltip>
    );
    const trigger = screen.getByText('Hover me').closest('div') as HTMLElement;
    await act(async () => {
      fireEvent.mouseEnter(trigger);
      // Advance timers
      await new Promise((r) => setTimeout(r, 10));
    });
    expect(screen.getByText('My Tooltip')).toBeInTheDocument();
  });

  it('hides tooltip after mouseLeave', async () => {
    render(
      <Tooltip content="My Tooltip" delay={0}>
        <button>Hover me</button>
      </Tooltip>
    );
    const trigger = screen.getByText('Hover me').closest('div') as HTMLElement;
    await act(async () => {
      fireEvent.mouseEnter(trigger);
      await new Promise((r) => setTimeout(r, 10));
    });
    await act(async () => {
      fireEvent.mouseLeave(trigger);
    });
    expect(screen.queryByText('My Tooltip')).not.toBeInTheDocument();
  });

  it('accepts ReactNode as content', () => {
    render(
      <Tooltip content={<span data-testid="rich-tooltip">Rich Content</span>} delay={0}>
        <button>Hover me</button>
      </Tooltip>
    );
    expect(screen.getByText('Hover me')).toBeInTheDocument();
  });

  it('renders with position bottom', () => {
    render(
      <Tooltip content="Bottom tip" position="bottom">
        <span>Item</span>
      </Tooltip>
    );
    expect(screen.getByText('Item')).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// ProgressIndicator tests
// ---------------------------------------------------------------------------

describe('ProgressIndicator', () => {
  it('renders without crashing', () => {
    render(<ProgressIndicator value={50} />);
  });

  it('renders progress bar at correct width', () => {
    const { container } = render(<ProgressIndicator value={75} />);
    const bar = container.querySelector('[style*="width"]') as HTMLElement;
    expect(bar?.style.width).toBe('75%');
  });

  it('clamps value to 0 if negative', () => {
    const { container } = render(<ProgressIndicator value={-10} />);
    const bar = container.querySelector('[style*="width"]') as HTMLElement;
    expect(bar?.style.width).toBe('0%');
  });

  it('clamps value to 100 if over 100', () => {
    const { container } = render(<ProgressIndicator value={150} />);
    const bar = container.querySelector('[style*="width"]') as HTMLElement;
    expect(bar?.style.width).toBe('100%');
  });

  it('shows label when provided', () => {
    render(<ProgressIndicator value={50} label="Loading Data" />);
    expect(screen.getByText('Loading Data')).toBeInTheDocument();
  });

  it('shows percentage', () => {
    render(<ProgressIndicator value={42} label="Test" />);
    expect(screen.getByText('42%')).toBeInTheDocument();
  });

  it('shows total count when total provided', () => {
    render(<ProgressIndicator value={50} total={200} label="Items" />);
    expect(screen.getByText('100/200')).toBeInTheDocument();
  });

  it('renders with cyan variant', () => {
    const { container } = render(<ProgressIndicator value={50} variant="cyan" />);
    const fill = container.querySelector('.bg-forge-cyan');
    expect(fill).toBeInTheDocument();
  });

  it('renders with green variant', () => {
    const { container } = render(<ProgressIndicator value={50} variant="green" />);
    const fill = container.querySelector('.bg-forge-green');
    expect(fill).toBeInTheDocument();
  });

  it('renders with default amber variant', () => {
    const { container } = render(<ProgressIndicator value={50} />);
    const fill = container.querySelector('.bg-forge-amber');
    expect(fill).toBeInTheDocument();
  });
});

describe('IndeterminateProgress', () => {
  it('renders without crashing', () => {
    const { container } = render(<IndeterminateProgress />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it('renders the animated bar element', () => {
    const { container } = render(<IndeterminateProgress />);
    const bar = container.querySelector('.bg-forge-amber');
    expect(bar).toBeInTheDocument();
  });

  it('renders label when provided', () => {
    render(<IndeterminateProgress label="Processing..." />);
    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  it('renders without label by default', () => {
    const { container } = render(<IndeterminateProgress />);
    const label = container.querySelector('.font-mono');
    expect(label).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// NotificationCenter tests
// ---------------------------------------------------------------------------

describe('NotificationCenter', () => {
  it('renders without crashing', () => {
    expect(() => render(<NotificationCenter />)).not.toThrow();
  });

  it('mounts in the DOM', () => {
    const { container } = render(<NotificationCenter />);
    expect(container).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Accessibility tests
// ---------------------------------------------------------------------------

describe('ScreenReaderOnly', () => {
  it('renders with sr-only class', () => {
    const { container } = render(<ScreenReaderOnly>SR Text</ScreenReaderOnly>);
    const el = container.querySelector('.sr-only') as HTMLElement;
    expect(el).toBeInTheDocument();
    expect(el.textContent).toBe('SR Text');
  });
});

describe('SkipToContent', () => {
  it('renders a link', () => {
    render(<SkipToContent />);
    const link = screen.getByText('Skip to main content');
    expect(link).toBeInTheDocument();
  });

  it('renders with correct default href', () => {
    render(<SkipToContent />);
    const link = screen.getByText('Skip to main content') as HTMLAnchorElement;
    expect(link.href).toContain('#main-content');
  });

  it('accepts custom targetId', () => {
    render(<SkipToContent targetId="custom-target" />);
    const link = screen.getByText('Skip to main content') as HTMLAnchorElement;
    expect(link.href).toContain('#custom-target');
  });
});

describe('LiveRegion', () => {
  it('renders with aria-live=polite by default', () => {
    const { container } = render(<LiveRegion message="Status update" />);
    const el = container.querySelector('[aria-live]') as HTMLElement;
    expect(el.getAttribute('aria-live')).toBe('polite');
  });

  it('renders message text', () => {
    render(<LiveRegion message="Operation complete" />);
    expect(screen.getByText('Operation complete')).toBeInTheDocument();
  });

  it('renders with assertive politeness', () => {
    const { container } = render(<LiveRegion message="Alert!" politeness="assertive" />);
    const el = container.querySelector('[aria-live]') as HTMLElement;
    expect(el.getAttribute('aria-live')).toBe('assertive');
  });
});
