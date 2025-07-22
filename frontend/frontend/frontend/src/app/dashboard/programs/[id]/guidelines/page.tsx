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

interface AIGuideline {
  id: number;
  section: string;
  weight: number;
  criteria: any;
  is_active: boolean;
  version: number;
  created_at: string;
}

export default function ProgramGuidelinesPage() {
  const params = useParams();
  const router = useRouter();
  const programId = params.id as string;
  
  const [program, setProgram] = useState<Program | null>(null);
  const [guidelines, setGuidelines] = useState<AIGuideline[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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

      // Load existing guidelines for this program
      // API needs to be updated to support program filtering
      const guidelinesResponse = await apiService.get(`/ai-guidelines/programs/${programId}`);
      if (guidelinesResponse.success) {
        setGuidelines(guidelinesResponse.guidelines || []);
      }

    } catch (error: any) {
      setError(error.message || 'Failed to load guidelines data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateGuidelines = async () => {
    setGenerating(true);
    setError(null);
    setSuccess(null);

    try {
      // Generate guidelines based on program-specific calibration
      const response = await apiService.post(`/ai-guidelines/programs/${programId}/generate`, {});
      
      if (response.success) {
        setSuccess('AI Guidelines generated successfully!');
        loadProgramData(); // Reload to show new guidelines
      } else {
        setError(response.error || 'Failed to generate guidelines');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to generate guidelines');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading guidelines...</div>
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
              <h1 className="text-3xl font-bold text-gray-900">AI Guidelines</h1>
              <p className="mt-2 text-gray-600">
                Manage AI scoring guidelines for <strong>{program.name}</strong>
              </p>
            </div>
            <button
              onClick={handleGenerateGuidelines}
              disabled={generating}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
            >
              {generating ? 'Generating...' : 'Generate Guidelines'}
            </button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
            {success}
          </div>
        )}

        {/* Program-Scoped Guidelines */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Program-Specific AI Guidelines
            </h3>
            <p className="text-gray-600 mb-6">
              This is the program-specific AI guidelines management for {program.name}.
              Guidelines generated here will only apply to applications for this program.
            </p>
            <div className="bg-indigo-50 border border-indigo-200 rounded-md p-4 max-w-md mx-auto">
              <p className="text-sm text-indigo-800">
                <strong>Program Context:</strong> Guidelines will be generated based on the 
                calibration answers specific to this program, ensuring each program has 
                its own unique scoring criteria.
              </p>
            </div>

            {guidelines.length > 0 && (
              <div className="mt-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">
                  Current Guidelines ({guidelines.length} sections)
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
                  {guidelines.map((guideline) => (
                    <div key={guideline.id} className="p-4 bg-gray-50 rounded-lg text-left">
                      <h5 className="font-medium text-gray-900">{guideline.section}</h5>
                      <p className="text-sm text-gray-600">Weight: {guideline.weight}</p>
                      <p className="text-xs text-gray-500">v{guideline.version}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}