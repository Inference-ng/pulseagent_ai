import { useState, useEffect, useCallback } from 'react';

/**
 * useFullscreen
 * Wraps the browser Fullscreen API (with webkit/ms prefix fallbacks).
 * Works on iOS 16.4+ via the webkit prefixed API.
 */
export function useFullscreen() {
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Keep state in sync with Escape key / browser UI exits
  useEffect(() => {
    const onChange = () => {
      const el =
        document.fullscreenElement ||
        (document as any).webkitFullscreenElement ||
        (document as any).msFullscreenElement;
      setIsFullscreen(!!el);
    };

    document.addEventListener('fullscreenchange', onChange);
    document.addEventListener('webkitfullscreenchange', onChange);
    document.addEventListener('msfullscreenchange', onChange);

    return () => {
      document.removeEventListener('fullscreenchange', onChange);
      document.removeEventListener('webkitfullscreenchange', onChange);
      document.removeEventListener('msfullscreenchange', onChange);
    };
  }, []);

  const enter = useCallback(() => {
    const el = document.documentElement as any;
    if (el.requestFullscreen) return el.requestFullscreen();
    if (el.webkitRequestFullscreen) return el.webkitRequestFullscreen();
    if (el.msRequestFullscreen) return el.msRequestFullscreen();
  }, []);

  const exit = useCallback(() => {
    const doc = document as any;
    if (doc.exitFullscreen) return doc.exitFullscreen();
    if (doc.webkitExitFullscreen) return doc.webkitExitFullscreen();
    if (doc.msExitFullscreen) return doc.msExitFullscreen();
  }, []);

  const toggle = useCallback(() => {
    isFullscreen ? exit() : enter();
  }, [isFullscreen, enter, exit]);

  /** True when the browser supports the Fullscreen API at all */
  const isSupported =
    typeof document !== 'undefined' &&
    !!(
      document.documentElement.requestFullscreen ||
      (document.documentElement as any).webkitRequestFullscreen ||
      (document.documentElement as any).msRequestFullscreen
    );

  return { isFullscreen, toggle, isSupported };
}
