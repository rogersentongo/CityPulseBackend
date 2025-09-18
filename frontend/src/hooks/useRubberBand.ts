import { useState, useEffect, useCallback } from 'react';

export function useRubberBand() {
  const [isAtTop, setIsAtTop] = useState(false);
  const [isAtBottom, setIsAtBottom] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleScroll = useCallback(() => {
    const scrollTop = window.scrollY;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;

    setIsAtTop(scrollTop === 0);
    setIsAtBottom(scrollTop + windowHeight >= documentHeight - 10);
  }, []);

  const handleTouchStart = useCallback((e: TouchEvent) => {
    if (isAtTop) {
      const startY = e.touches[0].clientY;

      const handleTouchMove = (moveEvent: TouchEvent) => {
        const currentY = moveEvent.touches[0].clientY;
        const distance = Math.max(0, currentY - startY);
        setPullDistance(Math.min(distance / 3, 100)); // Damping
      };

      const handleTouchEnd = () => {
        if (pullDistance > 50) {
          setIsRefreshing(true);
        }
        setPullDistance(0);
        document.removeEventListener('touchmove', handleTouchMove);
        document.removeEventListener('touchend', handleTouchEnd);
      };

      document.addEventListener('touchmove', handleTouchMove);
      document.addEventListener('touchend', handleTouchEnd);
    }
  }, [isAtTop, pullDistance]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    document.addEventListener('touchstart', handleTouchStart);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      document.removeEventListener('touchstart', handleTouchStart);
    };
  }, [handleScroll, handleTouchStart]);

  return {
    isAtTop,
    isAtBottom,
    pullDistance,
    isRefreshing,
    setIsRefreshing,
  };
}