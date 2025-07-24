'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function QuestionnairesPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to program selection - questionnaires are program-specific
    // This enforces the program-centric architecture
    router.replace('/dashboard/programs');
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-pulse text-lg text-gray-700">Redirecting to program selection...</div>
        <div className="text-sm text-gray-500 mt-2">Questionnaires are managed within specific programs</div>
      </div>
    </div>
  );
}