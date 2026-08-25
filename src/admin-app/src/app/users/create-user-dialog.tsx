'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage } from '@/lib/api-error';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus } from 'lucide-react';

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';

interface CreateUserPayload {
  email: string;
  password: string;
  full_name?: string;
  is_admin: boolean;
}

export function CreateUserDialog() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [isAdmin, setIsAdmin] = useState('false');

  const createUser = useMutation({
    mutationFn: async (payload: CreateUserPayload) => {
      const res = await apiClient.post('/admin/users', payload);
      return res.data;
    },
    onSuccess: (_data, payload) => {
      toast.success(`User ${payload.email} created`);
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
      setOpen(false);
      setEmail('');
      setFullName('');
      setPassword('');
      setIsAdmin('false');
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });

  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const passwordValid = password.length >= 8 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /\d/.test(password);
  const canSubmit = emailValid && passwordValid && !createUser.isPending;

  const handleSubmit = () => {
    if (!canSubmit) {
      toast.error('Enter a valid email and a strong password (8+ chars, upper, lower, digit)');
      return;
    }
    void createUser.mutateAsync({
      email: email.trim(),
      password,
      full_name: fullName.trim() || undefined,
      is_admin: isAdmin === 'true',
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button><Plus className="ms-2 h-4 w-4" />Add User</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add User</DialogTitle>
          <DialogDescription>Create a new platform user account</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label htmlFor="cu-email" className="text-sm font-medium">Email</label>
            <Input id="cu-email" type="email" placeholder="user@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cu-name" className="text-sm font-medium">Full name</label>
            <Input id="cu-name" placeholder="Jane Doe" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cu-password" className="text-sm font-medium">Password</label>
            <Input id="cu-password" type="password" placeholder="Min 8 chars, mixed case, digit" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cu-role" className="text-sm font-medium">Role</label>
            <select id="cu-role" className={selectClass} value={isAdmin} onChange={(e) => setIsAdmin(e.target.value)}>
              <option value="false">User</option>
              <option value="true">Admin</option>
            </select>
          </div>
          <Button className="w-full" onClick={handleSubmit} disabled={!canSubmit}>
            {createUser.isPending ? 'Creating...' : 'Create User'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
