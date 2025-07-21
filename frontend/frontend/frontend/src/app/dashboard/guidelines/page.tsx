'use client';

import { useState, useEffect } from 'react';
import { apiService } from '../../../services/api';

interface ScoringGuide {
  '1-3': string;
  '4-5': string;
  '6-7': string;
  '8-10': string;
}

interface GuidelineCategory {
  section: string;
  name: string;
  weight: number;
  criteria: string[];
  red_flags: string[];
  scoring_guide: ScoringGuide;
}

interface Guidelines {
  categories: GuidelineCategory[];
}

interface SavedGuidelines {
  id: number;
  program_id: number;
  guidelines: Guidelines;
  version: number;
  is_active: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export default function GuidelinesPage() {
  const [guidelines, setGuidelines] = useState<Guidelines | null>(null);
  const [guidelinesHistory, setGuidelinesHistory] = useState<SavedGuidelines[]>([]);
  const [activeVersion, setActiveVersion] = useState<number | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isActivating, setIsActivating] = useState(false);
  const [selectedModel, setSelectedModel] = useState('claude-3.5-sonnet');
  const [showJsonPreview, setShowJsonPreview] = useState(false);
  const [editedGuidelines, setEditedGuidelines] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [programs, setPrograms] = useState<any[]>([]);
  const [selectedProgramId, setSelectedProgramId] = useState<number | null>(null);

  // Use selected program ID, fallback to first program
  const programId = selectedProgramId || programs[0]?.id || 1;

  const supportedModels = [
    { value: 'claude-3.5-sonnet', label: 'Claude 3.5 Sonnet' },
    { value: 'claude-3-opus', label: 'Claude 3 Opus' },
    { value: 'claude-3-haiku', label: 'Claude 3 Haiku' },
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini' }
  ];

  useEffect(() => {
    loadPrograms();
  }, []);

  useEffect(() => {
    if (programId) {
      loadGuidelinesHistory();
      loadActiveGuidelines();
    }
  }, [programId]);

  useEffect(() => {
    if (guidelines) {
      setEditedGuidelines(JSON.stringify(guidelines, null, 2));
    }
  }, [guidelines]);

  const loadPrograms = async () => {
    try {
      const response = await apiService.get('/organizations/programs');
      if (response && Array.isArray(response)) {
        setPrograms(response);
        // Auto-select first program if none selected
        if (response.length > 0 && !selectedProgramId) {
          setSelectedProgramId(response[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to load programs:', error);
      // Fallback to mock data for testing
      const mockPrograms = [
        { id: 1, name: 'TechEd Accelerator 2024', description: 'Main accelerator program' },
        { id: 2, name: 'Healthcare Innovation Track', description: 'Specialized healthcare program' }
      ];
      setPrograms(mockPrograms);
      setSelectedProgramId(1);
    }
  };

  const loadGuidelinesHistory = async () => {
    try {
      const response = await apiService.get(`/ai-guidelines/history?program_id=${programId}`);
      if (response.success) {
        setGuidelinesHistory(response.guidelines || []);
        setActiveVersion(response.active_version);
      }
    } catch (error) {
      console.error('Failed to load guidelines history:', error);
    }
  };

  const loadActiveGuidelines = async () => {
    try {
      const response = await apiService.get(`/ai-guidelines/active?program_id=${programId}`);
      if (response) {
        setGuidelines(response.guidelines);
      }
    } catch (error) {
      console.error('Failed to load active guidelines:', error);
    }
  };

  const handleGenerateGuidelines = async () => {
    setIsGenerating(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await apiService.post(`/ai-guidelines/generate?program_id=${programId}`, {
        calibration_data: {}, // Empty object - service will fetch from database
        model: selectedModel
      });

      if (response.success && response.guidelines) {
        setGuidelines(response.guidelines);
        setSuccess(`Guidelines generated successfully using ${response.model_used}`);
      } else {
        setError(response.error || 'Failed to generate guidelines');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to generate guidelines');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveGuidelines = async (activateImmediately = false) => {
    if (!guidelines) return;

    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      // If in edit mode, parse the edited JSON
      let guidelinesToSave = guidelines;
      if (showJsonPreview && editedGuidelines) {
        guidelinesToSave = JSON.parse(editedGuidelines);
      }

      const response = await apiService.post(`/ai-guidelines/save?program_id=${programId}`, {
        guidelines: guidelinesToSave,
        is_active: activateImmediately,
        notes: activateImmediately ? 'Saved and activated immediately' : 'Saved as draft'
      });

      if (response.success) {
        setSuccess(`Guidelines ${activateImmediately ? 'saved and activated' : 'saved as draft'} successfully`);
        loadGuidelinesHistory();
        if (activateImmediately) {
          loadActiveGuidelines();
        }
      } else {
        setError(response.error || 'Failed to save guidelines');
      }
    } catch (error: any) {
      if (error.name === 'SyntaxError') {
        setError('Invalid JSON format. Please check your edits.');
      } else {
        setError(error.message || 'Failed to save guidelines');
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleActivateVersion = async (version: number) => {
    setIsActivating(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await apiService.post(`/ai-guidelines/activate?program_id=${programId}`, {
        version: version
      });

      if (response.success) {
        setSuccess(`Version ${version} activated successfully`);
        setActiveVersion(version);
        loadGuidelinesHistory();
        loadActiveGuidelines();
      } else {
        setError(response.error || 'Failed to activate version');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to activate version');
    } finally {
      setIsActivating(false);
    }
  };

  const renderGuidelines = (guidelines: Guidelines) => {
    return (
      <div className="space-y-6">
        {guidelines.categories.map((category, index) => (
          <div key={category.section} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-500">Weight:</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {category.weight}/10
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Evaluation Criteria</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {category.criteria.map((criterion, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="inline-block w-2 h-2 bg-green-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                      {criterion}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Red Flags</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {category.red_flags.map((flag, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="inline-block w-2 h-2 bg-red-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="mt-4 p-4 bg-gray-50 rounded-md">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Scoring Guide</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                <div>
                  <span className="font-medium text-red-700">1-3:</span>
                  <p className="text-gray-600 text-xs mt-1">{category.scoring_guide['1-3']}</p>
                </div>
                <div>
                  <span className="font-medium text-yellow-700">4-5:</span>
                  <p className="text-gray-600 text-xs mt-1">{category.scoring_guide['4-5']}</p>
                </div>
                <div>
                  <span className="font-medium text-blue-700">6-7:</span>
                  <p className="text-gray-600 text-xs mt-1">{category.scoring_guide['6-7']}</p>
                </div>
                <div>
                  <span className="font-medium text-green-700">8-10:</span>
                  <p className="text-gray-600 text-xs mt-1">{category.scoring_guide['8-10']}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI Guidelines Management</h1>
          <p className="mt-2 text-gray-600">Generate and manage AI scoring guidelines based on your calibration preferences</p>
          
          {/* Program Selector */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Select Program</label>
            <select
              value={selectedProgramId || ''}
              onChange={(e) => setSelectedProgramId(parseInt(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white min-w-64"
            >
              <option value="">Select a program...</option>
              {programs.map(program => (
                <option key={program.id} value={program.id}>
                  {program.name}
                </option>
              ))}
            </select>
            {selectedProgramId && (
              <p className="text-xs text-gray-500 mt-1">
                Program ID: {selectedProgramId}
              </p>
            )}
          </div>
        </div>

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

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          <div className="xl:col-span-3">
            {/* Generation and Preview Section */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate Guidelines</h2>
              
              <div className="flex items-center space-x-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">AI Model</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {supportedModels.map(model => (
                      <option key={model.value} value={model.value}>{model.label}</option>
                    ))}
                  </select>
                </div>
                
                <div className="flex-1"></div>
                
                <button
                  onClick={handleGenerateGuidelines}
                  disabled={isGenerating}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isGenerating ? 'Generating...' : 'Generate Guidelines'}
                </button>
              </div>

              {guidelines && (
                <div className="border-t pt-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Generated Guidelines</h3>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setShowJsonPreview(!showJsonPreview)}
                        className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
                      >
                        {showJsonPreview ? 'Visual View' : 'JSON Edit'}
                      </button>
                      <button
                        onClick={() => handleSaveGuidelines(false)}
                        disabled={isSaving}
                        className="px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 disabled:opacity-50"
                      >
                        {isSaving ? 'Saving...' : 'Save Draft'}
                      </button>
                      <button
                        onClick={() => handleSaveGuidelines(true)}
                        disabled={isSaving}
                        className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 disabled:opacity-50"
                      >
                        {isSaving ? 'Saving...' : 'Save & Activate'}
                      </button>
                    </div>
                  </div>

                  {showJsonPreview ? (
                    <div>
                      <textarea
                        value={editedGuidelines}
                        onChange={(e) => setEditedGuidelines(e.target.value)}
                        className="w-full h-96 font-mono text-sm border border-gray-300 rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Edit guidelines JSON..."
                      />
                    </div>
                  ) : (
                    renderGuidelines(guidelines)
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="xl:col-span-1">
            {/* Guidelines History Sidebar */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Guidelines History</h3>
              
              {guidelinesHistory.length === 0 ? (
                <p className="text-gray-500 text-sm">No guidelines generated yet.</p>
              ) : (
                <div className="space-y-3">
                  {guidelinesHistory.map((savedGuidelines) => (
                    <div
                      key={savedGuidelines.version}
                      className={`p-3 rounded-md border ${
                        savedGuidelines.is_active 
                          ? 'border-green-200 bg-green-50' 
                          : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-900">
                          Version {savedGuidelines.version}
                        </span>
                        {savedGuidelines.is_active && (
                          <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                            Active
                          </span>
                        )}
                      </div>
                      
                      <p className="text-xs text-gray-600 mb-2">
                        {savedGuidelines.guidelines.categories.length} categories
                      </p>
                      
                      <p className="text-xs text-gray-500">
                        {new Date(savedGuidelines.created_at).toLocaleDateString()}
                      </p>

                      {!savedGuidelines.is_active && (
                        <button
                          onClick={() => handleActivateVersion(savedGuidelines.version)}
                          disabled={isActivating}
                          className="mt-2 w-full px-2 py-1 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                        >
                          {isActivating ? 'Activating...' : 'Activate'}
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}