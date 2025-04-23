"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

interface CloseIconProps {
  className?: string;
}

/**
 * CloseIcon component that adapts to the current theme.
 * Provides better visibility in dark mode with stronger contrast.
 */
export function CloseIcon({ className = "" }: CloseIconProps) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch by only rendering after mount
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Return a placeholder with the same dimensions during SSR
    return (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
        <path
          d="M3.33398 3.33334L12.6673 12.6667M12.6673 3.33334L3.33398 12.6667"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="square"
        />
      </svg>
    );
  }

  // Determine stroke color and width based on theme
  const isDark = resolvedTheme === "dark";
  const strokeWidth = isDark ? 2.5 : 2;
  
  return (
    <svg 
      width="16" 
      height="16" 
      viewBox="0 0 16 16" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M3.33398 3.33334L12.6673 12.6667M12.6673 3.33334L3.33398 12.6667"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeOpacity={isDark ? 1 : 0.9}
      />
    </svg>
  );
}
