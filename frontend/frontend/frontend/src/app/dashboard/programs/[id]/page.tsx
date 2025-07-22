'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiService } from '../../../../services/api';

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

export default function ProgramDetailPage() {
  const params = useParams();
  const router = useRouter();
  const programId = params.id as string;
  
  const [program, setProgram] = useState<Program | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (programId) {
      loadProgram();
    }
  }, [programId]);

  const loadProgram = async () => {
    try {
      const response = await apiService.get(`/programs/${programId}`);
      if (response.success) {
        setProgram(response.program);
      } else {
        setError(response.error || 'Failed to load program');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to load program');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading program...</div>
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

  const getSetupSteps = () => [
    {
      name: 'Build Questionnaire',
      description: 'Create application questions for startups',
      completed: program.questionnaire_count > 0,
      link: `/dashboard/programs/${program.id}/questionnaires`,
      icon: '📝',
      color: 'green'
    },
    {
      name: 'Complete Calibration',
      description: 'Set your accelerator preferences',
      completed: program.calibration_completion >= 100,
      link: `/dashboard/programs/${program.id}/calibration`,
      icon: '🎯',
      color: 'yellow'
    },
    {
      name: 'Generate AI Guidelines',
      description: 'AI-powered scoring criteria',
      completed: program.has_active_guidelines,
      link: `/dashboard/programs/${program.id}/guidelines`,
      icon: '🤖',
      color: 'indigo'
    },
    {
      name: 'Review Applications',
      description: 'Manage startup applications',
      completed: program.application_count > 0,
      link: `/dashboard/programs/${program.id}/applications`,
      icon: '📊',
      color: 'purple'
    }
  ];

  const setupSteps = getSetupSteps();
  const completedSteps = setupSteps.filter(step => step.completed).length;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/dashboard/programs"
            className="text-blue-600 hover:text-blue-800 text-sm font-medium mb-4 inline-block"
          >
            ← Back to Programs
          </Link>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{program.name}</h1>
              {program.description && (
                <p className="mt-2 text-gray-600">{program.description}</p>
              )}
              <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                <span>Created {new Date(program.created_at).toLocaleDateString()}</span>
                <span>•</span>
                <span>Program ID: {program.id}</span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {!program.is_active && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                  Inactive
                </span>
              )}
              <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
                Edit Program
              </button>
            </div>
          </div>
        </div>

        {/* Progress Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Setup Progress</h2>
            <span className="text-sm text-gray-600">
              {completedSteps} of {setupSteps.length} completed
            </span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${(completedSteps / setupSteps.length) * 100}%` }}
            ></div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {setupSteps.map((step, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-2 ${
                  step.completed
                    ? 'border-green-200 bg-green-50'
                    : 'border-gray-200 bg-gray-50'
                } transition-colors`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-2xl mr-3">{step.icon}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900">{step.name}</h3>
                      <p className="text-sm text-gray-600">{step.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {step.completed ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        ✓ Complete
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        Pending
                      </span>
                    )}
                  </div>
                </div>
                
                {step.link !== '#' && (
                  <div className="mt-3">
                    <Link
                      href={step.link}
                      className={`inline-flex items-center px-3 py-1 rounded-md text-sm font-medium ${
                        step.completed
                          ? 'bg-green-100 text-green-700 hover:bg-green-200'
                          : `bg-${step.color}-100 text-${step.color}-700 hover:bg-${step.color}-200`
                      }`}
                    >
                      {step.completed ? 'Review' : 'Start Setup'}
                    </Link>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-md">
                <span className="text-xl">📝</span>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">{program.questionnaire_count}</p>
                <p className="text-sm text-gray-600">Questionnaires</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-md">
                <span className="text-xl">🎯</span>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">
                  {Math.round(program.calibration_completion)}%
                </p>
                <p className="text-sm text-gray-600">Calibration</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-indigo-100 rounded-md">
                <span className="text-xl">🤖</span>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">
                  {program.has_active_guidelines ? 'Active' : 'None'}
                </p>
                <p className="text-sm text-gray-600">AI Guidelines</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-md">
                <span className="text-xl">📊</span>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">{program.application_count}</p>
                <p className="text-sm text-gray-600">Applications</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Program Management</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Link
              href={`/dashboard/programs/${program.id}/questionnaires`}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center">
                <span className="text-2xl mr-3">📝</span>
                <div>
                  <h3 className="font-medium text-gray-900">Questionnaire Builder</h3>
                  <p className="text-sm text-gray-600">Create and manage application forms</p>
                </div>
              </div>
            </Link>

            <Link
              href={`/dashboard/programs/${program.id}/calibration`}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center">
                <span className="text-2xl mr-3">🎯</span>
                <div>
                  <h3 className="font-medium text-gray-900">Calibration Settings</h3>
                  <p className="text-sm text-gray-600">Configure accelerator preferences</p>
                </div>
              </div>
            </Link>

            <Link
              href={`/dashboard/programs/${program.id}/guidelines`}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center">
                <span className="text-2xl mr-3">🤖</span>
                <div>
                  <h3 className="font-medium text-gray-900">AI Guidelines</h3>
                  <p className="text-sm text-gray-600">Manage scoring guidelines</p>
                </div>
              </div>
            </Link>

            <Link
              href={`/dashboard/programs/${program.id}/applications`}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center">
                <span className="text-2xl mr-3">📊</span>
                <div>
                  <h3 className="font-medium text-gray-900">Applications</h3>
                  <p className="text-sm text-gray-600">Review and manage applications</p>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}