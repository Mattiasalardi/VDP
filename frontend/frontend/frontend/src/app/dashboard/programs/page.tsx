'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiService } from '../../../services/api';

interface Program {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  organization_id: number;
  created_at: string;
  updated_at: string;
  questionnaire_count: number;
  calibration_completion: number;
  has_active_guidelines: boolean;
  application_count: number;
}

export default function ProgramsPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showInactive, setShowInactive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Create program form
  const [createForm, setCreateForm] = useState({
    name: '',
    description: '',
    is_active: true
  });
  const [isCreating, setIsCreating] = useState(false);

  const router = useRouter();

  useEffect(() => {
    loadPrograms();
  }, [showInactive]);

  const loadPrograms = async () => {
    try {
      const response = await apiService.get(`/programs?include_inactive=${showInactive}`);
      if (response.success) {
        setPrograms(response.programs || []);
      } else {
        setError(response.error || 'Failed to load programs');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to load programs');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProgram = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await apiService.post('/programs', createForm);
      if (response.success) {
        setSuccess('Program created successfully!');
        setShowCreateModal(false);
        setCreateForm({ name: '', description: '', is_active: true });
        loadPrograms();
      } else {
        setError(response.error || 'Failed to create program');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to create program');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteProgram = async (programId: number) => {
    if (!confirm('Are you sure you want to delete this program? This will deactivate it.')) {
      return;
    }

    try {
      const response = await apiService.delete(`/programs/${programId}`);
      if (response.success) {
        setSuccess('Program deleted successfully');
        loadPrograms();
      } else {
        setError(response.error || 'Failed to delete program');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to delete program');
    }
  };

  const getCompletionStatus = (program: Program) => {
    const steps = [
      { name: 'Questionnaire', complete: program.questionnaire_count > 0 },
      { name: 'Calibration', complete: program.calibration_completion >= 100 },
      { name: 'Guidelines', complete: program.has_active_guidelines },
      { name: 'Applications', complete: program.application_count > 0 }
    ];
    
    const completedSteps = steps.filter(step => step.complete).length;
    return { steps, completedSteps, totalSteps: steps.length };
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading programs...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/dashboard"
            className="text-blue-600 hover:text-blue-800 text-sm font-medium mb-4 inline-block"
          >
            ← Back to Dashboard
          </Link>
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Program Management</h1>
              <p className="mt-2 text-gray-600">Create and manage your accelerator programs</p>
            </div>
            <div className="flex items-center space-x-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={showInactive}
                  onChange={(e) => setShowInactive(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-600">Show inactive</span>
              </label>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Create Program
              </button>
            </div>
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

        {/* Programs Grid */}
        {programs.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg mb-4">No programs found</div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium"
            >
              Create Your First Program
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {programs.map((program) => {
              const status = getCompletionStatus(program);
              return (
                <div
                  key={program.id}
                  className={`bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow ${
                    !program.is_active ? 'opacity-60 border-gray-300' : 'border-gray-200'
                  }`}
                >
                  {/* Program Header */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {program.name}
                        {!program.is_active && (
                          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            Inactive
                          </span>
                        )}
                      </h3>
                      {program.description && (
                        <p className="text-sm text-gray-600">{program.description}</p>
                      )}
                    </div>
                  </div>

                  {/* Progress Status */}
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">Setup Progress</span>
                      <span className="text-sm text-gray-500">
                        {status.completedSteps}/{status.totalSteps}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${(status.completedSteps / status.totalSteps) * 100}%` }}
                      ></div>
                    </div>
                    <div className="mt-2 grid grid-cols-2 gap-1">
                      {status.steps.map((step, idx) => (
                        <div key={idx} className="flex items-center">
                          <div
                            className={`w-2 h-2 rounded-full mr-2 ${
                              step.complete ? 'bg-green-400' : 'bg-gray-300'
                            }`}
                          ></div>
                          <span className="text-xs text-gray-600">{step.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Statistics */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900">
                        {program.questionnaire_count}
                      </div>
                      <div className="text-xs text-gray-500">Questionnaires</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900">
                        {program.application_count}
                      </div>
                      <div className="text-xs text-gray-500">Applications</div>
                    </div>
                  </div>

                  {/* Calibration Status */}
                  <div className="mb-4 p-3 bg-gray-50 rounded-md">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700">Calibration</span>
                      <span className="text-sm text-gray-600">
                        {Math.round(program.calibration_completion)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-yellow-500 h-1.5 rounded-full"
                        style={{ width: `${program.calibration_completion}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <Link
                      href={`/dashboard/programs/${program.id}`}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Manage
                    </Link>
                    <button
                      onClick={() => handleDeleteProgram(program.id)}
                      className="px-3 py-2 border border-red-300 text-red-700 hover:bg-red-50 rounded-md text-sm font-medium"
                    >
                      Delete
                    </button>
                  </div>

                  {/* Meta Info */}
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-500">
                      Created {new Date(program.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Create Program Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-semibold mb-4">Create New Program</h2>
              
              <form onSubmit={handleCreateProgram}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Program Name *
                  </label>
                  <input
                    type="text"
                    value={createForm.name}
                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., TechEd Accelerator 2024"
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
                    placeholder="Brief description of this program..."
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
                    {isCreating ? 'Creating...' : 'Create Program'}
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