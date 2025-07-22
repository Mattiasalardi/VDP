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

interface CalibrationQuestion {
  key: string;
  question: string;
  type: string;
  options?: string[];
  category: string;
}

interface CalibrationAnswer {
  question_key: string;
  answer_value: any;
  answer_text: string;
}

export default function ProgramCalibrationPage() {
  const params = useParams();
  const router = useRouter();
  const programId = params.id as string;
  
  const [program, setProgram] = useState<Program | null>(null);
  const [questions, setQuestions] = useState<CalibrationQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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

      // Load calibration questions
      const questionsResponse = await apiService.get('/calibration/questions');
      if (questionsResponse.success) {
        setQuestions(questionsResponse.questions || []);
      }

      // Load existing calibration answers for this program
      // API needs to be updated to include program ID
      const statusResponse = await apiService.get(`/calibration/programs/${programId}/status`);
      if (statusResponse.success && statusResponse.answers) {
        const answerMap: Record<string, any> = {};
        statusResponse.answers.forEach((answer: CalibrationAnswer) => {
          answerMap[answer.question_key] = answer.answer_value;
        });
        setAnswers(answerMap);
      }

    } catch (error: any) {
      setError(error.message || 'Failed to load calibration data');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionKey: string, value: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionKey]: value
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      // Convert answers to API format
      const answersToSave = Object.entries(answers).map(([questionKey, answerValue]) => ({
        question_key: questionKey,
        answer_value: answerValue,
        program_id: parseInt(programId)
      }));

      // Save answers (API needs to be updated for program scoping)
      const response = await apiService.post('/calibration/answers/batch', {
        answers: answersToSave
      });

      if (response.success) {
        setSuccess('Calibration answers saved successfully!');
      } else {
        setError(response.error || 'Failed to save calibration answers');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to save calibration answers');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading calibration...</div>
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
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
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
              <h1 className="text-3xl font-bold text-gray-900">Accelerator Calibration</h1>
              <p className="mt-2 text-gray-600">
                Configure preferences for <strong>{program.name}</strong> to generate AI scoring guidelines
              </p>
            </div>
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Settings'}
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

        {/* Program-Scoped Calibration */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Program-Specific Calibration
            </h3>
            <p className="text-gray-600 mb-6">
              This is the program-specific calibration system for {program.name}.
              Your answers here will generate AI guidelines specific to this program.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4 max-w-md mx-auto">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> The calibration API endpoints need to be updated to support 
                program-specific context. Currently showing placeholder.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}