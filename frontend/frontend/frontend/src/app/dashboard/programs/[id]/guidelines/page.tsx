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
      const guidelinesResponse = await apiService.getGuidelinesHistory(parseInt(programId));
      if (guidelinesResponse.data && guidelinesResponse.data.guidelines) {
        setGuidelines(guidelinesResponse.data.guidelines);
      } else if (guidelinesResponse.error) {
        // If no guidelines exist yet, that's not an error
        if (!guidelinesResponse.error.includes('not found')) {
          setError(`Failed to load guidelines: ${guidelinesResponse.error}`);
        }
        setGuidelines([]);
      } else {
        setGuidelines([]);
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
      // Generate and save guidelines based on program-specific calibration
      const response = await apiService.generateAndSaveGuidelines(
        parseInt(programId), 
        "anthropic/claude-3.5-sonnet", 
        true, // activate immediately
        `Generated for program: ${program?.name}`
      );
      
      if (response.data && response.data.success) {
        setSuccess('AI Guidelines generated and activated successfully!');
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
        {guidelines.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No AI Guidelines Yet
              </h3>
              <p className="text-gray-600 mb-6">
                Generate AI scoring guidelines for <strong>{program.name}</strong> based on your calibration preferences.
                These guidelines will be used to automatically score startup applications.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4 max-w-lg mx-auto mb-6">
                <p className="text-sm text-blue-800">
                  <strong>How it works:</strong> AI analyzes your calibration answers to create custom 
                  scoring guidelines that match your program's priorities and preferences.
                </p>
              </div>
              <button
                onClick={handleGenerateGuidelines}
                disabled={generating}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium disabled:opacity-50"
              >
                {generating ? 'Generating Guidelines...' : 'Generate AI Guidelines'}
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Active AI Guidelines for {program.name}
              </h3>
              <p className="text-gray-600">
                {guidelines.length} scoring sections configured based on your calibration preferences.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {guidelines.map((guideline) => (
                <div key={guideline.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-medium text-gray-900">{guideline.section}</h5>
                    {guideline.is_active && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">Weight: {guideline.weight}/10</p>
                  <p className="text-xs text-gray-500">
                    Version {guideline.version} • {new Date(guideline.created_at).toLocaleDateString()}
                  </p>
                  {guideline.criteria && (
                    <div className="mt-2">
                      <p className="text-xs text-gray-600 truncate">
                        {typeof guideline.criteria === 'string' 
                          ? guideline.criteria.substring(0, 100) + '...'
                          : JSON.stringify(guideline.criteria).substring(0, 100) + '...'
                        }
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="mt-6 flex justify-between items-center">
              <div className="text-sm text-gray-600">
                Last updated: {guidelines.length > 0 ? new Date(guidelines[0].created_at).toLocaleDateString() : 'Never'}
              </div>
              <button
                onClick={handleGenerateGuidelines}
                disabled={generating}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
              >
                {generating ? 'Regenerating...' : 'Regenerate Guidelines'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}