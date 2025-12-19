// المسار: src/app/components/profile/ChangePasswordForm.tsx
'use client';

import { useState } from 'react';
import apiClient from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from "sonner";
import { Loader2 } from 'lucide-react';

export const ChangePasswordForm = () => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await apiClient.post('/api/users/me/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });

      toast.success("تم تغيير كلمة المرور بنجاح.");
      
      // مسح الحقول بعد النجاح
      setCurrentPassword('');
      setNewPassword('');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "فشل تغيير كلمة المرور. تأكد من كلمة المرور الحالية.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="currentPassword">كلمة المرور الحالية</Label>
        <Input 
          id="currentPassword" 
          type="password" 
          value={currentPassword} 
          onChange={(e) => setCurrentPassword(e.target.value)} 
          required 
          disabled={isLoading}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="newPassword">كلمة المرور الجديدة</Label>
        <Input 
          id="newPassword" 
          type="password" 
          value={newPassword} 
          onChange={(e) => setNewPassword(e.target.value)} 
          required 
          minLength={8}
          disabled={isLoading}
        />
         <p className="text-sm text-muted-foreground">يجب أن تكون 8 أحرف على الأقل.</p>
      </div>
      <Button type="submit" disabled={isLoading} className="w-full sm:w-auto">
        {isLoading && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
        {isLoading ? 'جارٍ التغيير...' : 'تغيير كلمة المرور'}
      </Button>
    </form>
  );
};