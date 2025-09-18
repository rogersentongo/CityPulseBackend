'use client';

import { useRouter } from 'next/navigation';
import { useAppStore } from '@/store';
import { AppLayout } from '@/components/layout/AppLayout';
import { VideoFeed } from '@/components/feed/VideoFeed';

export default function FeedPage() {
  const router = useRouter();
  const { userId, selectedBorough, isSetupComplete } = useAppStore();

  // Redirect if setup is not complete
  if (!isSetupComplete || !userId || !selectedBorough) {
    router.push('/');
    return null;
  }

  return (
    <AppLayout>
      <VideoFeed />
    </AppLayout>
  );
}