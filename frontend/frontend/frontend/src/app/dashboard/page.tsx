'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Organization {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export default function DashboardPage() {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchOrganization = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        router.push('/login');
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setOrganization(data);
        } else {
          localStorage.removeItem('access_token');
          localStorage.removeItem('organization_id');
          localStorage.removeItem('organization_name');
          router.push('/login');
        }
      } catch (error) {
        console.error('Error fetching organization:', error);
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    fetchOrganization();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('organization_id');
    localStorage.removeItem('organization_name');
    router.push('/login');
  };

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
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">VDP Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {organization?.name}
              </span>
              <Link
                href="/dashboard/settings"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Settings
              </Link>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Welcome to VDP Dashboard
              </h2>
              <p className="text-gray-600 mb-6">
                Venture Development Platform for {organization?.name}
              </p>
              
              <div className="bg-white rounded-lg shadow p-6 max-w-4xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Organization Details</h3>
                    <div className="space-y-2 text-left">
                      <div>
                        <span className="font-medium">Name:</span> {organization?.name}
                      </div>
                      <div>
                        <span className="font-medium">Email:</span> {organization?.email}
                      </div>
                      <div>
                        <span className="font-medium">Member since:</span>{' '}
                        {organization?.created_at ? new Date(organization.created_at).toLocaleDateString() : 'N/A'}
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                    <div className="space-y-2">
                      <button className="w-full text-left px-4 py-2 bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 transition-colors">
                        📋 Create New Program
                      </button>
                      <Link href="/dashboard/questionnaires" className="block w-full text-left px-4 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors">
                        📝 Build Questionnaire
                      </Link>
                      <Link href="/dashboard/calibration" className="block w-full text-left px-4 py-2 bg-yellow-50 text-yellow-700 rounded-md hover:bg-yellow-100 transition-colors">
                        🎯 Accelerator Calibration
                      </Link>
                      <Link href="/dashboard/guidelines" className="block w-full text-left px-4 py-2 bg-indigo-50 text-indigo-700 rounded-md hover:bg-indigo-100 transition-colors">
                        🤖 AI Scoring Guidelines
                      </Link>
                      <button className="w-full text-left px-4 py-2 bg-purple-50 text-purple-700 rounded-md hover:bg-purple-100 transition-colors">
                        📊 View Reports
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-8">
                <p className="text-sm text-gray-500">
                  Phase 2 Task 2.1 Complete - Authentication system is working!
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}