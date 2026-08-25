'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage, getDependentsConflict, type DependentsConflict } from '@/lib/api-error';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from '@/components/ui/dialog';
import { Trash2 } from 'lucide-react';

interface DeleteButtonProps {
  endpoint: string;
  label: string;
  queryKeys: string[];
  /** Extra confirmation text; defaults to the generic confirm. */
  confirmText?: string;
}

/** Trash icon button that deletes a resource, upgrading a 409
 *  dependent-conflict into a Force-delete dialog. Rendered by the
 *  skills/resources/categories/job-roles admin tables. */
export function DeleteButton({ endpoint, label, queryKeys, confirmText }: DeleteButtonProps) {
  const queryClient = useQueryClient();
  const [conflict, setConflict] = useState<DependentsConflict | null>(null);
  const [pending, setPending] = useState(false);

  const remove = useMutation({
    mutationFn: async (force: boolean) => {
      await apiClient.delete(force ? `${endpoint}?force=true` : endpoint);
    },
    onSuccess: (_data, force) => {
      toast.success(`${label} deleted`);
      setConflict(null);
      queryKeys.forEach((key) => queryClient.invalidateQueries({ queryKey: [key] }));
      if (force) toast.info(`All dependent references were cleaned up`);
    },
    onError: (error) => {
      const dependents = getDependentsConflict(error);
      if (dependents) setConflict(dependents);
      else toast.error(getApiErrorMessage(error));
    },
  });

  const handleDelete = async () => {
    if (!confirm(confirmText || `Delete this ${label}?`)) return;
    setPending(true);
    await remove.mutateAsync(false).catch(() => undefined);
    setPending(false);
  };

  const dependentEntries = Object.entries(conflict?.dependents || {});

  return (
    <>
      <Button variant="ghost" size="icon" onClick={handleDelete} disabled={pending} className="text-destructive">
        <Trash2 className="h-4 w-4" />
      </Button>
      <Dialog open={conflict !== null} onOpenChange={(open) => !open && setConflict(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cannot delete {label}</DialogTitle>
            <DialogDescription>{conflict?.message || 'This item is still referenced.'}</DialogDescription>
          </DialogHeader>
          <div className="rounded-md border p-3 text-sm">
            <p className="mb-2 font-medium">Referenced by:</p>
            <ul className="list-disc space-y-1 ps-5">
              {dependentEntries.map(([table, count]) => (
                <li key={table}>{count} &times; {table.replaceAll('_', ' ')}</li>
              ))}
            </ul>
            <p className="mt-2 text-xs text-muted-foreground">
              Force delete removes the {label} and cleans up these references (linked rows are deleted or detached per the schema rules).
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConflict(null)}>Cancel</Button>
            <Button variant="destructive" disabled={remove.isPending} onClick={() => void remove.mutateAsync(true)}>
              {remove.isPending ? 'Deleting...' : 'Force delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}