'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface Question {
  id: number;
  question_type: 'text' | 'multiple_choice' | 'scale' | 'file_upload';
  text: string;
  options: any;
  is_required: boolean;
  order_index: number;
  validation_rules?: any;
}

interface Application {
  id: number;
  unique_id: string;
  startup_name: string;
  contact_email: string;
  is_submitted: boolean;
  program_id: number;
  program_name: string;
}

interface Questionnaire {
  id: number;
  name: string;
  description: string;
  questions: Question[];
}

export default function PublicApplicationForm() {
  const params = useParams();
  const router = useRouter();
  const programId = params.programId as string;
  const applicationId = params.applicationId as string;
  
  const [application, setApplication] = useState<Application | null>(null);
  const [questionnaire, setQuestionnaire] = useState<Questionnaire | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  
  // Form responses
  const [responses, setResponses] = useState<Record<number, any>>({});
  const [errors, setErrors] = useState<Record<number, string>>({});
  
  useEffect(() => {
    if (applicationId && programId) {
      loadQuestionnaire();
    }
  }, [applicationId, programId]);

  const loadQuestionnaire = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/public/applications/${applicationId}/questionnaire?program_id=${programId}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Additional validation: ensure application belongs to the program in URL
          if (data.application.program_id !== parseInt(programId)) {
            setError('Invalid application link - program mismatch');
            return;
          }
          
          setApplication(data.application);
          setQuestionnaire(data.questionnaire);
        } else {
          setError(data.error || 'Failed to load application form');
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load application form');
      }
    } catch (error: any) {
      setError('Unable to connect to server. Please try again later.');
      console.error('Error loading questionnaire:', error);
    } finally {
      setLoading(false);
    }
  };

  const validateQuestion = (question: Question, value: any): string | null => {
    // Check if required
    if (question.is_required && (!value || (Array.isArray(value) && value.length === 0))) {
      return 'This field is required';
    }

    // Type-specific validation
    switch (question.question_type) {
      case 'text':
        if (value && question.validation_rules) {
          if (question.validation_rules.min_length && value.length < question.validation_rules.min_length) {
            return `Minimum ${question.validation_rules.min_length} characters required`;
          }
          if (question.validation_rules.max_length && value.length > question.validation_rules.max_length) {
            return `Maximum ${question.validation_rules.max_length} characters allowed`;
          }
        }
        break;
      
      case 'multiple_choice':
        // Validation handled by required check above
        break;
      
      case 'scale':
        if (value && question.options) {
          const numValue = Number(value);
          const min = question.options.min_value || 1;
          const max = question.options.max_value || 10;
          if (numValue < min || numValue > max) {
            return `Value must be between ${min} and ${max}`;
          }
        }
        break;
      
      case 'file_upload':
        // File validation will be handled separately
        break;
    }

    return null;
  };

  const handleResponseChange = (questionId: number, value: any) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: value
    }));
    
    // Clear error for this question
    if (errors[questionId]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[questionId];
        return newErrors;
      });
    }
  };

  const validateCurrentStep = (): boolean => {
    if (!questionnaire) return false;
    
    const question = questionnaire.questions[currentStep];
    const value = responses[question.id];
    const error = validateQuestion(question, value);
    
    if (error) {
      setErrors(prev => ({
        ...prev,
        [question.id]: error
      }));
      return false;
    }
    
    return true;
  };

  const handleNext = () => {
    if (validateCurrentStep()) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    // Validate all questions
    if (!questionnaire) return;
    
    const newErrors: Record<number, string> = {};
    let hasErrors = false;
    
    for (const question of questionnaire.questions) {
      const value = responses[question.id];
      const error = validateQuestion(question, value);
      if (error) {
        newErrors[question.id] = error;
        hasErrors = true;
      }
    }
    
    if (hasErrors) {
      setErrors(newErrors);
      setCurrentStep(0); // Go back to first question with error
      return;
    }
    
    setSubmitting(true);
    
    try {
      // TODO: Implement submission endpoint
      console.log('Submitting responses:', responses);
      
      // For now, show success message
      alert('Application submitted successfully!');
      
    } catch (error: any) {
      setError('Failed to submit application. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-lg text-gray-700">Loading application form...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="text-center">
            <div className="text-red-500 text-5xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Unable to Load Form</h1>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={loadQuestionnaire}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!application || !questionnaire) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-gray-500 text-lg">Application not found</div>
        </div>
      </div>
    );
  }

  const currentQuestion = questionnaire.questions[currentStep];
  const isLastStep = currentStep === questionnaire.questions.length - 1;
  const progress = ((currentStep + 1) / questionnaire.questions.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6 mb-4 sm:mb-6">
          <div className="text-center">
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
              {questionnaire.name}
            </h1>
            <p className="text-sm sm:text-base text-gray-600 mb-4">
              {application.program_name}
            </p>
            {questionnaire.description && (
              <p className="text-sm text-gray-500">
                {questionnaire.description}
              </p>
            )}
          </div>
          
          {/* Progress Bar */}
          <div className="mt-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Question {currentStep + 1} of {questionnaire.questions.length}</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Question Form */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6 mb-4 sm:mb-6">
          <div className="mb-4 sm:mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-sm font-medium text-gray-500">
                Question {currentStep + 1}
              </span>
              {currentQuestion.is_required && (
                <span className="text-red-500 text-sm">*</span>
              )}
            </div>
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4">
              {currentQuestion.text}
            </h2>
          </div>

          {/* Render Question Input */}
          <div className="mb-6">
            <QuestionInput
              question={currentQuestion}
              value={responses[currentQuestion.id]}
              onChange={(value) => handleResponseChange(currentQuestion.id, value)}
              error={errors[currentQuestion.id]}
            />
          </div>

          {/* Navigation */}
          <div className="flex flex-col sm:flex-row justify-between gap-3 sm:gap-0">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
            >
              Previous
            </button>
            
            {isLastStep ? (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md font-medium disabled:opacity-50 text-sm sm:text-base"
              >
                {submitting ? 'Submitting...' : 'Submit Application'}
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium text-sm sm:text-base"
              >
                Next
              </button>
            )}
          </div>
        </div>

        {/* Application Info */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="text-center text-xs sm:text-sm text-gray-500">
            <div className="break-words">Application for: <strong>{application.startup_name}</strong></div>
            <div className="break-words">Email: {application.contact_email}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Question Input Component
interface QuestionInputProps {
  question: Question;
  value: any;
  onChange: (value: any) => void;
  error?: string;
}

function QuestionInput({ question, value, onChange, error }: QuestionInputProps) {
  const renderInput = () => {
    switch (question.question_type) {
      case 'text':
        return question.options?.multiline ? (
          <textarea
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={question.options?.placeholder || 'Enter your answer...'}
            maxLength={question.options?.max_length || 500}
            rows={4}
            className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
          />
        ) : (
          <input
            type="text"
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={question.options?.placeholder || 'Enter your answer...'}
            maxLength={question.options?.max_length || 500}
            className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
          />
        );

      case 'multiple_choice':
        const isMultiple = question.options?.multiple_selection;
        const selectedValues = Array.isArray(value) ? value : (value ? [value] : []);
        
        return (
          <div className="space-y-3">
            {(question.options?.choices || []).map((choice: string, index: number) => (
              <label key={index} className="flex items-center space-x-3 cursor-pointer">
                <input
                  type={isMultiple ? 'checkbox' : 'radio'}
                  name={`question-${question.id}`}
                  checked={selectedValues.includes(choice)}
                  onChange={(e) => {
                    if (isMultiple) {
                      const newValues = e.target.checked
                        ? [...selectedValues, choice]
                        : selectedValues.filter(v => v !== choice);
                      onChange(newValues);
                    } else {
                      onChange(choice);
                    }
                  }}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
                <span className="text-gray-700">{choice}</span>
              </label>
            ))}
            
            {question.options?.other_option && (
              <div className="flex items-center space-x-3">
                <input
                  type={isMultiple ? 'checkbox' : 'radio'}
                  name={`question-${question.id}`}
                  checked={selectedValues.some(v => v.startsWith('Other:'))}
                  onChange={(e) => {
                    if (e.target.checked) {
                      const otherValue = `Other: ${(value?.other_text || '')}`;
                      if (isMultiple) {
                        onChange([...selectedValues.filter(v => !v.startsWith('Other:')), otherValue]);
                      } else {
                        onChange(otherValue);
                      }
                    } else {
                      if (isMultiple) {
                        onChange(selectedValues.filter(v => !v.startsWith('Other:')));
                      } else {
                        onChange('');
                      }
                    }
                  }}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
                <span className="text-gray-700">Other:</span>
                <input
                  type="text"
                  placeholder="Please specify..."
                  value={selectedValues.find(v => v.startsWith('Other:'))?.replace('Other: ', '') || ''}
                  onChange={(e) => {
                    const otherValue = `Other: ${e.target.value}`;
                    if (isMultiple) {
                      const filtered = selectedValues.filter(v => !v.startsWith('Other:'));
                      onChange(e.target.value ? [...filtered, otherValue] : filtered);
                    } else {
                      onChange(e.target.value ? otherValue : '');
                    }
                  }}
                  className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
          </div>
        );

      case 'scale':
        const min = question.options?.min_value || 1;
        const max = question.options?.max_value || 10;
        const step = question.options?.step || 1;
        const values = [];
        for (let i = min; i <= max; i += step) {
          values.push(i);
        }
        
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center text-sm text-gray-600">
              <span>{question.options?.min_label || min}</span>
              <span>{question.options?.max_label || max}</span>
            </div>
            <div className="flex justify-between">
              {values.map((val) => (
                <label key={val} className="flex flex-col items-center cursor-pointer">
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={val}
                    checked={Number(value) === val}
                    onChange={(e) => onChange(Number(e.target.value))}
                    className="h-4 w-4 text-blue-600 border-gray-300"
                  />
                  <span className="text-sm text-gray-600 mt-1">{val}</span>
                </label>
              ))}
            </div>
            {value && (
              <div className="text-center text-lg font-medium text-blue-600">
                Selected: {value}
              </div>
            )}
          </div>
        );

      case 'file_upload':
        return (
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <div className="text-gray-400 mb-2">
                <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <p className="text-gray-600 mb-2">
                {question.options?.multiple_files ? 'Drop files here or click to upload' : 'Drop file here or click to upload'}
              </p>
              <p className="text-sm text-gray-500">
                Max size: {question.options?.max_size_mb || 10}MB • 
                Types: {(question.options?.allowed_extensions || ['.pdf']).join(', ')}
              </p>
              <input
                type="file"
                multiple={question.options?.multiple_files}
                accept={(question.options?.allowed_extensions || ['.pdf']).join(',')}
                onChange={(e) => onChange(e.target.files)}
                className="mt-4 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
            {value && value.length > 0 && (
              <div className="text-sm text-gray-600">
                Selected: {Array.from(value).map((f: any) => f.name).join(', ')}
              </div>
            )}
          </div>
        );

      default:
        return <div className="text-gray-500">Question type not supported</div>;
    }
  };

  return (
    <div>
      {renderInput()}
      {error && (
        <div className="mt-2 text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  );
}