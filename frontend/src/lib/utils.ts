/**
 * Utility functions for SwasthyaAI frontend
 */

import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export function formatTimestamp(date: Date): string {
  return new Intl.DateTimeFormat('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }).format(date);
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date);
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

export function getSafetyColor(level: string): string {
  switch (level) {
    case 'emergency':
    case 'critical':
      return 'text-red-600 dark:text-red-400';
    case 'urgent':
    case 'high':
      return 'text-orange-600 dark:text-orange-400';
    case 'caution':
    case 'medium':
      return 'text-amber-600 dark:text-amber-400';
    case 'safe':
    case 'low':
      return 'text-green-600 dark:text-green-400';
    default:
      return 'text-slate-600 dark:text-slate-400';
  }
}

export function getSafetyBgColor(level: string): string {
  switch (level) {
    case 'emergency':
    case 'critical':
      return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
    case 'urgent':
    case 'high':
      return 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800';
    case 'caution':
    case 'medium':
      return 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800';
    case 'safe':
    case 'low':
      return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
    default:
      return 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700';
  }
}

export function getStatusBadge(status: string): { label: string; className: string } {
  switch (status) {
    case 'thinking':
      return { label: 'Analyzing…', className: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' };
    case 'awaiting_input':
      return { label: 'Needs Input', className: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300' };
    case 'completed':
      return { label: 'Complete', className: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' };
    case 'error':
      return { label: 'Error', className: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' };
    case 'escalated':
      return { label: 'Escalated', className: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' };
    default:
      return { label: 'Ready', className: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300' };
  }
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

export function isValidSessionId(sessionId: string): boolean {
  return /^[a-zA-Z0-9-_]{8,}$/.test(sessionId);
}