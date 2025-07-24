'use client';

import { useEffect, useState } from 'react';
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
  type: 'scale' | 'multiple_choice' | 'text';
  description: string;
  scale_min?: number;
  scale_max?: number;
  scale_labels?: { [key: number]: string };
  options?: Array<{ value: string; label: string }>;
  placeholder?: string;
  max_length?: number;
}

interface CalibrationCategory {
  title: string;
  description: string;
  questions: CalibrationQuestion[];
}

interface CalibrationAnswer {
  question_key: string;
  answer_value: any;
  answer_text?: string;
}

interface CalibrationStatus {
  is_complete: boolean;
  total_questions: number;
  answered_questions: number;
  completion_percentage: number;
  missing_questions: string[];
  next_category?: string;
}

export default function ProgramCalibrationPage() {
  const params = useParams();
  const router = useRouter();
  const programId = parseInt(params.id as string);
  
  const [program, setProgram] = useState<Program | null>(null);
  const [categories, setCategories] = useState<{ [key: string]: CalibrationCategory }>({});
  const [answers, setAnswers] = useState<{ [key: string]: CalibrationAnswer }>({});
  const [status, setStatus] = useState<CalibrationStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [currentCategory, setCurrentCategory] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (programId) {
      loadProgramCalibrationData();
    }
  }, [programId]);

  const loadProgramCalibrationData = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      // Load program details
      const programResponse = await apiService.get(`/programs/${programId}`);
      if (programResponse.success) {
        setProgram(programResponse.program);
      } else {
        setError(programResponse.error || 'Failed to load program');
        return;
      }

      // Fetch calibration questions
      const questionsResult = await apiService.getCalibrationQuestions();
      if (questionsResult.error) {
        setError('Failed to load calibration questions');
        return;
      }

      // Fetch current session data (answers + status)
      const sessionResult = await apiService.getCalibrationSession(programId);
      if (sessionResult.error) {
        setError('Failed to load calibration session');
        return;
      }

      // Process questions data
      const questionsData = questionsResult.data;
      setCategories(questionsData.categories);

      // Set first category as current
      const categoryKeys = Object.keys(questionsData.categories);
      if (categoryKeys.length > 0) {
        setCurrentCategory(categoryKeys[0]);
      }

      // Process answers data
      const sessionData = sessionResult.data;
      const answersMap: { [key: string]: CalibrationAnswer } = {};
      sessionData.answers.forEach((answer: CalibrationAnswer) => {
        answersMap[answer.question_key] = answer;
      });
      setAnswers(answersMap);

      // Set status
      setStatus({
        is_complete: sessionData.completion_percentage === 100,
        total_questions: sessionData.total_questions,
        answered_questions: sessionData.answered_questions,
        completion_percentage: sessionData.completion_percentage,
        missing_questions: sessionData.missing_questions
      });

    } catch (error) {
      console.error('Error fetching calibration data:', error);
      setError('Failed to load calibration data');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionKey: string, answerValue: any, answerText?: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionKey]: {
        question_key: questionKey,
        answer_value: answerValue,
        answer_text: answerText
      }
    }));
  };

  const saveAnswer = async (questionKey: string) => {
    if (!answers[questionKey]) return;

    setSaving(true);
    try {
      const result = await apiService.createCalibrationAnswer(programId, answers[questionKey]);
      if (result.error) {
        setError(`Failed to save answer: ${result.error}`);
      }
    } catch (error) {
      console.error('Error saving answer:', error);
      setError('Failed to save answer');
    } finally {
      setSaving(false);
    }
  };

  const saveCategoryAnswers = async () => {
    const categoryQuestions = categories[currentCategory]?.questions || [];
    const categoryAnswers = categoryQuestions
      .map(q => answers[q.key])
      .filter(answer => answer);

    if (categoryAnswers.length === 0) return;

    setSaving(true);
    try {
      const result = await apiService.batchCreateCalibrationAnswers(programId, categoryAnswers);
      if (result.error) {
        setError(`Failed to save answers: ${result.error}`);
      } else {
        // Update status after successful save
        const statusResult = await apiService.getCalibrationStatus(programId);
        if (!statusResult.error) {
          setStatus(statusResult.data);
        }
      }
    } catch (error) {
      console.error('Error saving answers:', error);
      setError('Failed to save answers');
    } finally {
      setSaving(false);
    }
  };

  const renderQuestion = (question: CalibrationQuestion) => {
    const currentAnswer = answers[question.key];

    return (
      <div key={question.key} className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="mb-4">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {question.question}
          </h3>
          <p className="text-sm text-gray-600">{question.description}</p>
        </div>

        {question.type === 'scale' && (
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                {question.scale_labels?.[question.scale_min || 1] || question.scale_min || 1}
              </span>
              <input
                type="range"
                min={question.scale_min || 1}
                max={question.scale_max || 10}
                value={currentAnswer?.answer_value?.scale_value || question.scale_min || 1}
                onChange={(e) => {
                  const value = parseInt(e.target.value);
                  const label = question.scale_labels?.[value] || `${value}`;
                  handleAnswerChange(question.key, { scale_value: value }, label);
                }}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-sm text-gray-500">
                {question.scale_labels?.[question.scale_max || 10] || question.scale_max || 10}
              </span>
            </div>
            <div className="text-center">
              <span className="text-lg font-medium text-blue-600">
                {currentAnswer?.answer_value?.scale_value || question.scale_min || 1}
              </span>
              {question.scale_labels && (
                <p className="text-sm text-gray-600 mt-1">
                  {question.scale_labels[currentAnswer?.answer_value?.scale_value || question.scale_min || 1]}
                </p>
              )}
            </div>
          </div>
        )}

        {question.type === 'multiple_choice' && (
          <div className="space-y-3">
            {question.options?.map((option) => (
              <label key={option.value} className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name={question.key}
                  value={option.value}
                  checked={currentAnswer?.answer_value?.choice_value === option.value}
                  onChange={(e) => {
                    handleAnswerChange(question.key, { choice_value: e.target.value }, option.label);
                  }}
                  className="mt-1 h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-900">{option.label}</span>
              </label>
            ))}
          </div>
        )}

        {question.type === 'text' && (
          <div>
            <textarea
              placeholder={question.placeholder}
              maxLength={question.max_length}
              value={currentAnswer?.answer_value?.text_value || ''}
              onChange={(e) => {
                handleAnswerChange(question.key, { text_value: e.target.value }, e.target.value);
              }}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              rows={4}
            />
            {question.max_length && (
              <p className="text-xs text-gray-500 mt-1">
                {(currentAnswer?.answer_value?.text_value || '').length} / {question.max_length} characters
              </p>
            )}
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <button
            onClick={() => saveAnswer(question.key)}
            disabled={saving || !currentAnswer}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Answer'}
          </button>
        </div>
      </div>
    );
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

  const categoryKeys = Object.keys(categories);
  const currentCategoryIndex = categoryKeys.indexOf(currentCategory);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link 
                href={`/dashboard/programs/${programId}`} 
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back to {program.name}
              </Link>
              <h1 className="text-xl font-semibold text-gray-900">
                Accelerator Calibration - {program.name}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              {status && (
                <div className="text-sm text-gray-600">
                  Progress: {status.answered_questions}/{status.total_questions} questions ({Math.round(status.completion_percentage)}%)
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="flex space-x-8">
          {/* Category Navigation */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Categories</h2>
              <nav className="space-y-2">
                {categoryKeys.map((categoryKey) => {
                  const category = categories[categoryKey];
                  const categoryQuestions = category.questions || [];
                  const answeredInCategory = categoryQuestions.filter(q => answers[q.key]).length;
                  
                  return (
                    <button
                      key={categoryKey}
                      onClick={() => setCurrentCategory(categoryKey)}
                      className={`w-full text-left p-3 rounded-md text-sm ${
                        currentCategory === categoryKey
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium">{category.title}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {answeredInCategory}/{categoryQuestions.length} answered
                      </div>
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>

          {/* Current Category Questions */}
          <div className="flex-1">
            {currentCategory && categories[currentCategory] && (
              <div>
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {categories[currentCategory].title}
                  </h2>
                  <p className="text-gray-600 mt-1">
                    {categories[currentCategory].description}
                  </p>
                </div>

                <div className="space-y-6">
                  {categories[currentCategory].questions?.map(renderQuestion)}
                </div>

                <div className="mt-8 flex justify-between">
                  <button
                    onClick={() => {
                      if (currentCategoryIndex > 0) {
                        setCurrentCategory(categoryKeys[currentCategoryIndex - 1]);
                      }
                    }}
                    disabled={currentCategoryIndex === 0}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous Category
                  </button>

                  <button
                    onClick={saveCategoryAnswers}
                    disabled={saving}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : 'Save Category Progress'}
                  </button>

                  <button
                    onClick={() => {
                      if (currentCategoryIndex < categoryKeys.length - 1) {
                        setCurrentCategory(categoryKeys[currentCategoryIndex + 1]);
                      }
                    }}
                    disabled={currentCategoryIndex === categoryKeys.length - 1}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next Category
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}