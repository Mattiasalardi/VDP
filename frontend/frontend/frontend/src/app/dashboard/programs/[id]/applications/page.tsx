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

interface Application {
  id: number;
  unique_id: string;
  startup_name: string;
  contact_email: string;
  is_submitted: boolean;
  is_processed: boolean;
  processing_status: string;
  submitted_at?: string;
  processed_at?: string;
}

export default function ProgramApplicationsPage() {
  const params = useParams();
  const router = useRouter();
  const programId = params.id as string;
  
  const [program, setProgram] = useState<Program | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
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

      // Load program applications
      // API needs to be updated to support program filtering
      const applicationsResponse = await apiService.get(`/programs/${programId}/applications`);
      if (applicationsResponse.success) {
        setApplications(applicationsResponse.applications || []);
      }

    } catch (error: any) {
      setError(error.message || 'Failed to load applications data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading applications...</div>
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
              <h1 className="text-3xl font-bold text-gray-900">Applications</h1>
              <p className="mt-2 text-gray-600">
                Manage startup applications for <strong>{program.name}</strong>
              </p>
            </div>
            <div className="flex space-x-3">
              <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50">
                Export Data
              </button>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Generate Application Link
              </button>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-md">
                <span className="text-xl">📝</span>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">{applications.length}</p>
                <p className="text-sm text-gray-600">Total Applications</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-md">
                <span className="text-xl">✅</span>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">
                  {applications.filter(app => app.is_submitted).length}
                </p>
                <p className="text-sm text-gray-600">Submitted</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-md">
                <span className="text-xl">⚡</span>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">
                  {applications.filter(app => app.is_processed).length}
                </p>
                <p className="text-sm text-gray-600">Processed</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-md">
                <span className="text-xl">📊</span>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">
                  {applications.filter(app => app.processing_status === 'completed').length}
                </p>
                <p className="text-sm text-gray-600">Reports Ready</p>
              </div>
            </div>
          </div>
        </div>

        {/* Applications List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Program Applications</h3>
          </div>
          
          {applications.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📊</div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">
                No Applications Yet
              </h4>
              <p className="text-gray-600 mb-6">
                Applications submitted for {program.name} will appear here.
                Create a public application form to start collecting applications.
              </p>
              <div className="bg-purple-50 border border-purple-200 rounded-md p-4 max-w-md mx-auto">
                <p className="text-sm text-purple-800">
                  <strong>Next Phase:</strong> Phase 5 will implement the public application 
                  forms that startups will use to apply to this specific program.
                </p>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Startup
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Submitted
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {applications.map((application) => (
                    <tr key={application.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {application.startup_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {application.contact_email}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(application.processing_status)}`}>
                          {application.processing_status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {application.submitted_at 
                          ? new Date(application.submitted_at).toLocaleDateString()
                          : 'Not submitted'
                        }
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-blue-600 hover:text-blue-900 mr-4">
                          View Details
                        </button>
                        {application.is_processed && (
                          <button className="text-green-600 hover:text-green-900">
                            View Report
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}