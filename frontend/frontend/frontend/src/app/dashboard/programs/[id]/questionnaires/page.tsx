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
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    description: '',
    is_active: true
  });
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    if (programId) {
      loadProgramData();
    }
  }, [programId]);

  const loadProgramData = async () => {
    try {
      // Load program details - uses {success: true, program: {...}} format
      const programResponse = await apiService.get(`/programs/${programId}`);
      if (programResponse && programResponse.success && programResponse.program) {
        setProgram(programResponse.program);
      } else {
        setError('Failed to load program');
        return;
      }

      // Load program questionnaires - uses {questionnaires: [...]} format
      const questionnairesResponse = await apiService.get(`/questions/programs/${programId}/questionnaires`);
      if (questionnairesResponse && questionnairesResponse.questionnaires) {
        setQuestionnaires(questionnairesResponse.questionnaires);
      } else {
        console.log('No questionnaires found or failed to load');
        setQuestionnaires([]);
      }
      
    } catch (error: any) {
      setError(error.message || 'Failed to load program data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuestionnaire = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);
    setError(null);

    try {
      const questionnaire = await apiService.post(`/questions/programs/${programId}/questionnaires`, createForm);
      
      // The API returns the questionnaire directly
      if (questionnaire && questionnaire.id) {
        setShowCreateModal(false);
        setCreateForm({ name: '', description: '', is_active: true });
        loadProgramData(); // Reload questionnaires
        
        // Navigate to questionnaire builder
        router.push(`/dashboard/questionnaires/builder?id=${questionnaire.id}&programId=${programId}`);
      } else {
        setError('Failed to create questionnaire - invalid response');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to create questionnaire');
    } finally {
      setIsCreating(false);
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
            <button 
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Create Questionnaire
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {/* Questionnaires List */}
        {questionnaires.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📝</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No Questionnaires Yet
              </h3>
              <p className="text-gray-600 mb-6">
                Create your first questionnaire for <strong>{program.name}</strong> to start collecting startup applications.
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium"
              >
                Create Your First Questionnaire
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {questionnaires.map((questionnaire) => (
              <div
                key={questionnaire.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {questionnaire.name}
                      {!questionnaire.is_active && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Inactive
                        </span>
                      )}
                    </h3>
                    {questionnaire.description && (
                      <p className="text-sm text-gray-600">{questionnaire.description}</p>
                    )}
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-center text-sm text-gray-500">
                    <span className="font-medium">{questionnaire.question_count || 0}</span>
                    <span className="ml-1">questions</span>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    Created {new Date(questionnaire.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => router.push(`/dashboard/questionnaires/builder?id=${questionnaire.id}&programId=${programId}`)}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center px-3 py-2 rounded-md text-sm font-medium"
                  >
                    {questionnaire.question_count > 0 ? 'Edit' : 'Build'}
                  </button>
                  <button className="px-3 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-md text-sm font-medium">
                    •••
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Questionnaire Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-semibold mb-4">Create New Questionnaire</h2>
              
              <form onSubmit={handleCreateQuestionnaire}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Questionnaire Name *
                  </label>
                  <input
                    type="text"
                    value={createForm.name}
                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Application Form 2024"
                    required
                  />
                </div>
                
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={createForm.description}
                    onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 h-20"
                    placeholder="Brief description of this questionnaire..."
                  />
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isCreating}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isCreating ? 'Creating...' : 'Create & Build'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}