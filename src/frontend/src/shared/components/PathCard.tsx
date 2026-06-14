// src/frontend/src/shared/components/PathCard.tsx
'use client';

import Link from 'next/link';
import { memo, useCallback } from 'react';
import { usePrefetch } from '@/shared/api/usePrefetch';

type PathCardProps = {
  id: string;
  title: string;
  totalHours: number;
};

/**
 * PathCard - Memoized learning path card with intelligent prefetching
 * 
 * Performance improvements:
 * - React.memo prevents re-renders when parent updates with same props
 * - Intelligent prefetching on hover reduces perceived latency
 * - useCallback ensures stable callback reference
 */
const PathCard = memo(function PathCard({ id, title, totalHours }: PathCardProps) {
  const prefetch = usePrefetch();

  /**
   * Prefetch path details when user hovers over the card
   * This means data is likely cached before they click
   */
  const handleMouseEnter = useCallback(() => {
    prefetch.pathDetails(id);
  }, [prefetch, id]);

  return (
    <Link href={`/paths/${id}`} className="block">
      <div 
        className="bg-card p-6 rounded-lg border shadow hover:shadow-lg transition-shadow h-full cursor-pointer"
        onMouseEnter={handleMouseEnter}
      >
        <h3 className="text-xl font-bold text-primary">{title}</h3>
        <p className="text-muted-foreground mt-2">{totalHours} ساعة لإكماله</p>
      </div>
    </Link>
  );
});

export default PathCard;