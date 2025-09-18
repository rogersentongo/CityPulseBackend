'use client';

import { useRouter } from 'next/navigation';
import { useAppStore } from '@/store';
import { AppLayout } from '@/components/layout/AppLayout';
import { AskInterface } from '@/components/ask/AskInterface';

export default function AskPage() {
  const router = useRouter();
  const { userId, selectedBorough, isSetupComplete } = useAppStore();

  // Redirect if setup is not complete
  if (!isSetupComplete || !userId || !selectedBorough) {
    router.push('/');
    return null;
  }

  return (
    <AppLayout>
      <div className="min-h-screen p-4 pt-20">
        <AskInterface />
      </div>
    </AppLayout>
  );
}