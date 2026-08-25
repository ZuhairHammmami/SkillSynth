'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage } from '@/lib/api-error';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Pencil } from 'lucide-react';
import type { Profile } from '@/types/api';

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';

interface EditUserPayload {
  full_name?: string;
  is_admin?: boolean;
  password?: string;
}

/** Edit dialog for one admin-users row; PUTs /admin/users/{id} with the
 *  changed fields (blank password = unchanged). Rendered by users/page.tsx. */
export function EditUserDialog({ user }: { user: Profile }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [fullName, setFullName] = useState(user.full_name || '');
  const [isAdmin, setIsAdmin] = useState(String(user.is_admin));
  const [password, setPassword] = useState('');

  const updateUser = useMutation({
    mutationFn: async (payload: EditUserPayload) => {
      await apiClient.put(`/admin/users/${user.id}`, payload);
    },
    onSuccess: () => {
      toast.success('User updated');
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
      setOpen(false);
      setPassword('');
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });

  const passwordValid = password === '' || (password.length >= 8 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /\d/.test(password));
  const demotingSelf = user.is_admin && isAdmin === 'false';
  const canSubmit = passwordValid && !demotingSelf && !updateUser.isPending;

  const handleSubmit = () => {
    if (!passwordValid) {
      toast.error('Password must be 8+ chars with upper, lower and digit');
      return;
    }
    if (demotingSelf) {
      toast.error('You cannot revoke your own admin role');
      return;
    }
    void updateUser.mutateAsync({
      full_name: fullName.trim(),
      ...(isAdmin !== String(user.is_admin) ? { is_admin: isAdmin === 'true' } : {}),
      ...(password ? { password } : {}),
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button variant="ghost" size="icon" onClick={() => setOpen(true)}>
        <Pencil className="h-4 w-4" />
      </Button>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit User</DialogTitle>
          <DialogDescription>{user.email}</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label htmlFor={`eu-name-${user.id}`} className="text-sm font-medium">Full name</label>
            <Input id={`eu-name-${user.id}`} placeholder="Jane Doe" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor={`eu-role-${user.id}`} className="text-sm font-medium">Role</label>
            <select id={`eu-role-${user.id}`} className={selectClass} value={isAdmin} onChange={(e) => setIsAdmin(e.target.value)}>
              <option value="false">User</option>
              <option value="true">Admin</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <label htmlFor={`eu-pass-${user.id}`} className="text-sm font-medium">New password (optional)</label>
            <Input id={`eu-pass-${user.id}`} type="password" placeholder="Leave blank to keep current password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <Button className="w-full" onClick={handleSubmit} disabled={!canSubmit}>
            {updateUser.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}