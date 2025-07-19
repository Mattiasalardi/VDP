'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiService } from '../../../services/api';

interface GuidelinesCategory {
  name: string;
  weight: number;
  description: string;
  scoring_guidance: {
    high_score_indicators: string[];
    medium_score_indicators: string[];
    low_score_indicators: string[];
    key_questions: string[];
  };
}

interface Guidelines {
  categories: GuidelinesCategory[];
  overall_approach: {
    risk_tolerance: string;
    stage_focus: string;
    industry_focus: string;
    key_priorities: string[];
  };
  scoring_scale: {
    range: string;
    descriptions: { [key: string]: string };
  };
}

interface GuidelinesMetadata {
  program_id: number;
  organization_id: number;
  model: string;
  generated_at: string;
  calibration_questions_count: number;
  rate_limit_remaining: number;
}

interface CalibrationSummary {
  total_questions_answered: number;
  key_preferences: { [key: string]: string };
  risk_profile: string;
  stage_focus: string;
  industry_focus: string;
}

interface GeneratedGuidelines {
  guidelines: Guidelines;
  metadata: GuidelinesMetadata;
  calibration_summary: CalibrationSummary;
}

interface SavedGuidelines {
  id: number;
  program_id: number;
  guidelines: Guidelines;
  version: number;
  is_active: boolean;
  model_used: string;
  created_at: string;
  generated_at?: string;
}

export default function GuidelinesPage() {
  const [generatedGuidelines, setGeneratedGuidelines] = useState<GeneratedGuidelines | null>(null);
  const [activeGuidelines, setActiveGuidelines] = useState<SavedGuidelines | null>(null);
  const [guidelinesHistory, setGuidelinesHistory] = useState<SavedGuidelines[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>('');
  const [editMode, setEditMode] = useState(false);
  const [editedGuidelines, setEditedGuidelines] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState('anthropic/claude-3.5-sonnet');
  const router = useRouter();

  // Mock program ID - in real implementation, this would come from URL params or context
  const programId = 1;

  const availableModels = [
    { value: 'anthropic/claude-3.5-sonnet', label: 'Claude 3.5 Sonnet (Recommended)' },
    { value: 'anthropic/claude-3-opus', label: 'Claude 3 Opus (Most Capable)' },
    { value: 'anthropic/claude-3-haiku', label: 'Claude 3 Haiku (Fastest)' },
    { value: 'openai/gpt-4-turbo', label: 'GPT-4 Turbo' },
    { value: 'openai/gpt-4', label: 'GPT-4' }
  ];

  useEffect(() => {
    fetchActiveGuidelines();
    fetchGuidelinesHistory();
  }, []);

  const fetchActiveGuidelines = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const result = await apiService.getActiveGuidelines(programId);
      if (!result.error) {
        setActiveGuidelines(result.data);
      }
    } catch (error) {
      console.error('Error fetching active guidelines:', error);
    }
  };

  const fetchGuidelinesHistory = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const result = await apiService.getGuidelinesHistory(programId);
      if (!result.error) {
        setGuidelinesHistory(result.data.guidelines || []);
      }
    } catch (error) {
      console.error('Error fetching guidelines history:', error);
    }
  };

  const generateGuidelines = async () => {
    setGenerating(true);
    setError('');

    try {
      const result = await apiService.generateGuidelines(programId, selectedModel);
      if (result.error) {
        setError(result.error);
      } else {
        setGeneratedGuidelines(result.data);
        setEditedGuidelines(JSON.stringify(result.data.guidelines, null, 2));
      }
    } catch (error) {
      console.error('Error generating guidelines:', error);
      setError('Failed to generate guidelines');
    } finally {
      setGenerating(false);
    }
  };

  const saveGuidelines = async (approve: boolean = false) => {
    if (!generatedGuidelines) return;

    setSaving(true);
    setError('');

    try {
      let guidelinesData = generatedGuidelines;
      
      if (editMode && editedGuidelines) {
        try {
          const parsedGuidelines = JSON.parse(editedGuidelines);
          guidelinesData = {
            ...generatedGuidelines,
            guidelines: parsedGuidelines
          };
        } catch (e) {
          setError('Invalid JSON in edited guidelines');
          setSaving(false);
          return;
        }
      }

      const result = await apiService.saveGuidelines(programId, guidelinesData, approve);
      if (result.error) {
        setError(result.error);
      } else {
        if (approve) {
          setActiveGuidelines(result.data);
        }
        fetchGuidelinesHistory();
        setGeneratedGuidelines(null);
        setEditMode(false);
      }
    } catch (error) {
      console.error('Error saving guidelines:', error);
      setError('Failed to save guidelines');
    } finally {
      setSaving(false);
    }
  };

  const activateVersion = async (version: number) => {
    try {
      const result = await apiService.activateGuidelinesVersion(programId, version);
      if (!result.error) {
        fetchActiveGuidelines();
        fetchGuidelinesHistory();
      }
    } catch (error) {
      console.error('Error activating version:', error);
    }
  };

  const renderGuidelines = (guidelines: Guidelines) => {
    return (
      <div className="space-y-6">
        {/* Overall Approach */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Overall Approach</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <span className="font-medium text-blue-800">Risk Tolerance:</span>
              <span className="ml-2 text-blue-700 capitalize">{guidelines.overall_approach.risk_tolerance}</span>
            </div>
            <div>
              <span className="font-medium text-blue-800">Stage Focus:</span>
              <span className="ml-2 text-blue-700 capitalize">{guidelines.overall_approach.stage_focus.replace('_', ' ')}</span>
            </div>
            <div>
              <span className="font-medium text-blue-800">Industry Focus:</span>
              <span className="ml-2 text-blue-700 capitalize">{guidelines.overall_approach.industry_focus.replace('_', ' ')}</span>
            </div>
          </div>
          <div className="mt-3">
            <span className="font-medium text-blue-800">Key Priorities:</span>
            <ul className="ml-4 mt-1">
              {guidelines.overall_approach.key_priorities.map((priority, index) => (
                <li key={index} className="text-blue-700">• {priority}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Scoring Scale */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Scoring Scale ({guidelines.scoring_scale.range})</h3>
          <div className="space-y-2">
            {Object.entries(guidelines.scoring_scale.descriptions).map(([range, description]) => (
              <div key={range} className="flex">
                <span className="font-medium text-gray-700 w-16">{range}:</span>
                <span className="text-gray-600">{description}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Categories */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Evaluation Categories</h3>
          {guidelines.categories.map((category, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <h4 className="text-md font-medium text-gray-900">{category.name}</h4>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm font-medium">
                  Weight: {(category.weight * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-gray-600 mb-4">{category.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h5 className="font-medium text-green-700 mb-2">High Score Indicators</h5>
                  <ul className="text-sm text-green-600 space-y-1">
                    {category.scoring_guidance.high_score_indicators.map((indicator, idx) => (
                      <li key={idx}>• {indicator}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h5 className="font-medium text-red-700 mb-2">Low Score Indicators</h5>
                  <ul className="text-sm text-red-600 space-y-1">
                    {category.scoring_guidance.low_score_indicators.map((indicator, idx) => (
                      <li key={idx}>• {indicator}</li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <div className="mt-4">
                <h5 className="font-medium text-gray-700 mb-2">Key Questions</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  {category.scoring_guidance.key_questions.map((question, idx) => (
                    <li key={idx}>• {question}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                ← Back to Dashboard
              </Link>
              <h1 className="text-xl font-semibold text-gray-900">AI Scoring Guidelines</h1>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* Generate New Guidelines Section */}
          <div className="bg-white rounded-lg shadow mb-6 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Generate New Guidelines</h2>
            
            <div className="flex items-center space-x-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">AI Model</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="block w-64 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  {availableModels.map((model) => (
                    <option key={model.value} value={model.value}>
                      {model.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="pt-6">
                <button
                  onClick={generateGuidelines}
                  disabled={generating}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md text-sm font-medium disabled:opacity-50"
                >
                  {generating ? 'Generating...' : 'Generate Guidelines'}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}
          </div>

          {/* Generated Guidelines Preview */}
          {generatedGuidelines && (
            <div className="bg-white rounded-lg shadow mb-6">
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h2 className="text-lg font-medium text-gray-900">Generated Guidelines Preview</h2>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setEditMode(!editMode)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      {editMode ? 'Preview Mode' : 'Edit JSON'}
                    </button>
                  </div>
                </div>
                
                <div className="mt-2 text-sm text-gray-600">
                  Model: {generatedGuidelines.metadata.model} • 
                  Generated: {new Date(generatedGuidelines.metadata.generated_at).toLocaleString()} • 
                  Rate limit remaining: {generatedGuidelines.metadata.rate_limit_remaining}
                </div>
              </div>

              <div className="p-6">
                {editMode ? (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Edit Guidelines JSON:
                    </label>
                    <textarea
                      value={editedGuidelines}
                      onChange={(e) => setEditedGuidelines(e.target.value)}
                      className="w-full h-96 px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
                      placeholder="Edit the guidelines JSON..."
                    />
                  </div>
                ) : (
                  renderGuidelines(generatedGuidelines.guidelines)
                )}
              </div>

              <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
                <button
                  onClick={() => saveGuidelines(false)}
                  disabled={saving}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50"
                >
                  Save Draft
                </button>
                <button
                  onClick={() => saveGuidelines(true)}
                  disabled={saving}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Approve & Activate'}
                </button>
              </div>
            </div>
          )}

          {/* Active Guidelines */}
          {activeGuidelines && (
            <div className="bg-white rounded-lg shadow mb-6">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Currently Active Guidelines</h2>
                <div className="mt-2 text-sm text-gray-600">
                  Version {activeGuidelines.version} • 
                  Model: {activeGuidelines.model_used} • 
                  Created: {new Date(activeGuidelines.created_at).toLocaleString()}
                </div>
              </div>
              <div className="p-6">
                {renderGuidelines(activeGuidelines.guidelines)}
              </div>
            </div>
          )}

          {/* Guidelines History */}
          {guidelinesHistory.length > 0 && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Guidelines History</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {guidelinesHistory.map((guideline) => (
                    <div key={guideline.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="flex items-center space-x-3">
                            <span className="font-medium">Version {guideline.version}</span>
                            {guideline.is_active && (
                              <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">Active</span>
                            )}
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            Model: {guideline.model_used} • 
                            Created: {new Date(guideline.created_at).toLocaleString()}
                          </div>
                        </div>
                        {!guideline.is_active && (
                          <button
                            onClick={() => activateVersion(guideline.version)}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            Activate
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}