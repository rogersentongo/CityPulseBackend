'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/store';
import { AppLayout } from '@/components/layout/AppLayout';
import { VideoFeed } from '@/components/feed/VideoFeed';

export default function FeedPage() {
  const router = useRouter();
  const { userId, selectedBorough, isSetupComplete } = useAppStore();

  // Redirect if setup is not complete
  useEffect(() => {
    if (!isSetupComplete || !userId || !selectedBorough) {
      router.push('/');
    }
  }, [isSetupComplete, userId, selectedBorough, router]);

  // Show nothing while redirecting
  if (!isSetupComplete || !userId || !selectedBorough) {
    return null;
  }

  return (
    <AppLayout>
      <VideoFeed />
    </AppLayout>
  );
}