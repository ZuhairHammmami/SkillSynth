// src/shared/components/SkeletonLoading.tsx
'use client';

import React, { memo } from 'react';
import { Skeleton } from '@/shared/ui/skeleton';
import { cn } from '@/shared/lib/utils';

/**
 * PathCardSkeleton - Optimized skeleton for learning path cards
 * Used in dashboard to show perceived loading
 */
export const PathCardSkeleton = memo(function PathCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-sm p-4 space-y-4 border border-gray-200">
      {/* Title skeleton */}
      <Skeleton className="h-6 w-3/4" />
      
      {/* Description skeleton */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
      </div>
      
      {/* Footer skeleton */}
      <div className="flex justify-between pt-2">
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-8 w-24 rounded-md" />
      </div>
    </div>
  );
});

/**
 * DashboardGridSkeleton - Optimized grid of loading cards
 */
export const DashboardGridSkeleton = memo(function DashboardGridSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <PathCardSkeleton key={i} />
      ))}
    </div>
  );
});

/**
 * StepItemSkeleton - Optimized skeleton for path steps
 */
export const StepItemSkeleton = memo(function StepItemSkeleton() {
  return (
    <div className="bg-white rounded-lg p-4 space-y-3 border border-gray-200">
      {/* Icon and title */}
      <div className="flex gap-3 items-start">
        <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-5 w-2/3" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </div>

      {/* Content area */}
      <div className="space-y-2 pl-13">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
      </div>

      {/* Video player area skeleton */}
      <Skeleton className="h-64 w-full rounded-lg" />
    </div>
  );
});

/**
 * StepListSkeleton - Multiple steps loading skeleton
 */
export const StepListSkeleton = memo(function StepListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <StepItemSkeleton key={i} />
      ))}
    </div>
  );
});

/**
 * TableRowSkeleton - Optimized skeleton for table rows
 */
export const TableRowSkeleton = memo(function TableRowSkeleton({ columns = 4 }: { columns?: number }) {
  return (
    <tr className="border-b border-gray-200">
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  );
});

/**
 * TableSkeleton - Optimized skeleton for entire table
 */
export const TableSkeleton = memo(function TableSkeleton({ rows = 8, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <thead className="bg-gray-50 border-b border-gray-200">
        <tr>
          {Array.from({ length: columns }).map((_, i) => (
            <th key={i} className="px-4 py-3 text-left">
              <Skeleton className="h-4 w-20" />
            </th>
          ))}
        </tr>
      </thead>

      {/* Body */}
      <tbody>
        {Array.from({ length: rows }).map((_, i) => (
          <TableRowSkeleton key={i} columns={columns} />
        ))}
      </tbody>
    </div>
  );
});

/**
 * ProfileSkeleton - Optimized skeleton for profile page
 */
export const ProfileSkeleton = memo(function ProfileSkeleton() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Profile header */}
      <div className="flex gap-6 items-start">
        <Skeleton className="h-24 w-24 rounded-full flex-shrink-0" />
        <div className="space-y-3 flex-1">
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/3" />
        </div>
      </div>

      {/* Profile sections */}
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="space-y-3">
          <Skeleton className="h-6 w-1/4" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        </div>
      ))}
    </div>
  );
});

/**
 * WizardStepSkeleton - Optimized skeleton for wizard steps
 */
export const WizardStepSkeleton = memo(function WizardStepSkeleton() {
  return (
    <div className="space-y-6">
      {/* Step title */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="h-4 w-3/4" />
      </div>

      {/* Form fields */}
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-5 w-1/4" />
          <Skeleton className="h-10 w-full rounded-lg" />
        </div>
      ))}

      {/* Actions */}
      <div className="flex gap-2 justify-end pt-4">
        <Skeleton className="h-10 w-24 rounded-lg" />
        <Skeleton className="h-10 w-24 rounded-lg" />
      </div>
    </div>
  );
});

const Skeletons = {
  PathCardSkeleton,
  DashboardGridSkeleton,
  StepItemSkeleton,
  StepListSkeleton,
  TableRowSkeleton,
  TableSkeleton,
  ProfileSkeleton,
  WizardStepSkeleton,
};

export default Skeletons;
