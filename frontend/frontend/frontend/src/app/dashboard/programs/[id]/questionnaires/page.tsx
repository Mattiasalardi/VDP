'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiService } from '../../../../../services/api';

interface Program {
  id: number;
  name: string;
  description?: string;
}

interface Questionnaire {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  question_count?: number;
}

export default function ProgramQuestionnairesPage() {
  const params = useParams();
  const router = useRouter();
  const programId = params.id as string;
  
  const [program, setProgram] = useState<Program | null>(null);
  const [questionnaires, setQuestionnaires] = useState<Questionnaire[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (programId) {
      loadProgramData();
    }
  }, [programId]);

  const loadProgramData = async () => {
    try {
      // Load program details
      const programResponse = await apiService.get(`/programs/${programId}`);
      if (programResponse.success) {
        setProgram(programResponse.program);
      } else {
        setError(programResponse.error || 'Failed to load program');
        return;
      }

      // Load program questionnaires (API needs to be updated to support program filtering)
      // For now, this will show a placeholder until we implement program-scoped questionnaire API
      setQuestionnaires([]);
      
    } catch (error: any) {
      setError(error.message || 'Failed to load program data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading questionnaires...</div>
      </div>
    );
  }

  if (error || !program) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error || 'Program not found'}
          </div>
          <div className="mt-4">
            <Link
              href="/dashboard/programs"
              className="text-blue-600 hover:text-blue-800"
            >
              ← Back to Programs
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/dashboard/programs/${programId}`}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium mb-4 inline-block"
          >
            ← Back to {program.name}
          </Link>
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Questionnaires</h1>
              <p className="mt-2 text-gray-600">
                Manage questionnaires for <strong>{program.name}</strong>
              </p>
            </div>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium">
              Create Questionnaire
            </button>
          </div>
        </div>

        {/* Program-Scoped Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Program-Scoped Questionnaires
            </h3>
            <p className="text-gray-600 mb-6">
              This is the program-specific questionnaire builder for {program.name}.
              All questionnaires created here will only apply to this program.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 max-w-md mx-auto">
              <p className="text-sm text-yellow-800">
                <strong>Next Step:</strong> Implement program-scoped questionnaire API endpoints 
                and update this page to work with program context.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}