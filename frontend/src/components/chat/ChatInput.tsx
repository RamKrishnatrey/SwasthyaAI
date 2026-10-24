'use client';

import React, { useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
}

export function ChatInput({ onSend, disabled = false, placeholder = 'Describe your symptoms or health concern...', value, onChange }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [height, setHeight] = React.useState(52);

  // Auto-resize textarea
  const adjustHeight = useCallback(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const newHeight = Math.min(textareaRef.current.scrollHeight, 180);
      setHeight(newHeight);
      textareaRef.current.style.height = `${newHeight}px`;
    }
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const text = textareaRef.current?.value.trim();
    if (text && !disabled) {
      onSend(text);
      if (textareaRef.current) {
        textareaRef.current.value = '';
        setHeight(52);
        textareaRef.current.style.height = '52px';
      }
      onChange?.('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative flex items-end gap-2 p-4 bg-card border-t border-border">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={value ?? ''}
            onChange={(e) => {
              onChange?.(e.target.value);
              adjustHeight();
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={cn(
              'w-full px-4 py-3 pr-12 bg-muted border border-border rounded-xl',
              'text-base text-foreground placeholder:text-muted-foreground',
              'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'resize-none transition-colors',
              'min-h-[52px] max-h-[180px]'
            )}
            style={{ height: `${height}px` }}
            aria-label="Type your health concern"
            aria-describedby="input-hint"
          />
          <div id="input-hint" className="sr-only">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>

        <button
          type="submit"
          disabled={disabled || !value?.trim()}
          className={cn(
            'flex-shrink-0 p-3 rounded-xl transition-all duration-200',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
            disabled
              ? 'bg-muted text-muted-foreground cursor-not-allowed'
              : 'bg-primary text-white hover:bg-primary-hover active:scale-[0.98]'
          )}
          aria-label="Send message"
          aria-disabled={disabled || !value?.trim()}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      <p className="px-4 pb-3 text-xs text-muted-foreground text-center">
        Press <kbd className="px-1.5 py-0.5 bg-muted border border-border rounded text-[10px] font-mono">Enter</kbd> to send,
        <kbd className="px-1.5 py-0.5 bg-muted border border-border rounded text-[10px] font-mono">Shift+Enter</kbd> for new line
      </p>
    </form>
  );
}