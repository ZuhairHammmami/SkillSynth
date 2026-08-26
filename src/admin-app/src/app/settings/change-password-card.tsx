'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage } from '@/lib/api-error';
import { toast } from 'sonner';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { KeyRound } from 'lucide-react';

export function ChangePasswordCard() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const changePassword = useMutation({
    mutationFn: async (payload: { current_password: string; new_password: string }) => {
      await apiClient.post('/auth/change-password', payload);
    },
    onSuccess: () => {
      toast.success('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });

  const strongEnough =
    newPassword.length >= 8 && /[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword) && /\d/.test(newPassword);
  const canSubmit =
    currentPassword.length > 0 && strongEnough && newPassword === confirmPassword && !changePassword.isPending;

  const handleSubmit = () => {
    if (newPassword !== confirmPassword) {
      toast.error('New password and confirmation do not match');
      return;
    }
    if (!strongEnough) {
      toast.error('Password must be 8+ characters with uppercase, lowercase, and a digit');
      return;
    }
    void changePassword.mutateAsync({ current_password: currentPassword, new_password: newPassword });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <KeyRound className="h-4 w-4 text-muted-foreground" />
          Change Password
        </CardTitle>
        <CardDescription>Update your admin account password</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="max-w-sm space-y-4">
          <div className="space-y-1.5">
            <label htmlFor="cp-current" className="text-sm font-medium">Current password</label>
            <Input id="cp-current" type="password" autoComplete="current-password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cp-new" className="text-sm font-medium">New password</label>
            <Input id="cp-new" type="password" autoComplete="new-password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cp-confirm" className="text-sm font-medium">Confirm new password</label>
            <Input id="cp-confirm" type="password" autoComplete="new-password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
          </div>
          <Button onClick={handleSubmit} disabled={!canSubmit}>
            {changePassword.isPending ? 'Updating...' : 'Update Password'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
