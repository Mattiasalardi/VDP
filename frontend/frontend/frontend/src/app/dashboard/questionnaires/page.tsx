'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiService } from '../../../services/api';

interface Questionnaire {
  id: number;
  title: string;
  description: string;
  created_at: string;
  question_count: number;
}

export default function QuestionnairesPage() {
  const [questionnaires, setQuestionnaires] = useState<Questionnaire[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchQuestionnaires = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        router.push('/login');
        return;
      }

      try {
        const result = await apiService.getQuestionnaires();
        if (result.error) {
          console.error('Error fetching questionnaires:', result.error);
        } else {
          setQuestionnaires(result.data || []);
        }
      } catch (error) {
        console.error('Error fetching questionnaires:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestionnaires();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                ← Back to Dashboard
              </Link>
              <h1 className="text-xl font-semibold text-gray-900">Questionnaires</h1>
            </div>
            <div className="flex items-center">
              <Link
                href="/dashboard/questionnaires/builder"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Create New Questionnaire
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {questionnaires.length === 0 ? (
            <div className="text-center py-12">
              <div className="mx-auto h-12 w-12 text-gray-400">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No questionnaires</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by creating your first questionnaire.</p>
              <div className="mt-6">
                <Link
                  href="/dashboard/questionnaires/builder"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <svg className="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Create Questionnaire
                </Link>
              </div>
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {questionnaires.map((questionnaire) => (
                  <li key={questionnaire.id}>
                    <div className="px-4 py-4 flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-blue-600 truncate">
                              {questionnaire.title}
                            </p>
                            <p className="text-sm text-gray-500">{questionnaire.description}</p>
                            <p className="text-xs text-gray-400 mt-1">
                              {questionnaire.question_count} questions • Created {new Date(questionnaire.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="flex space-x-2">
                            <Link
                              href={`/dashboard/questionnaires/builder?id=${questionnaire.id}`}
                              className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                            >
                              Edit
                            </Link>
                            <Link
                              href={`/dashboard/questionnaires/${questionnaire.id}`}
                              className="text-gray-600 hover:text-gray-900 text-sm font-medium"
                            >
                              View
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}