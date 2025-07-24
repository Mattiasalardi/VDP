'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  TextQuestionBuilder,
  MultipleChoiceQuestionBuilder,
  ScaleQuestionBuilder,
  FileUploadQuestionBuilder
} from '../../../../components/QuestionBuilders';
import QuestionPreview from '../../../../components/QuestionPreview/QuestionPreview';
import { apiService } from '../../../../services/api';

interface Question {
  id?: number;
  question_type: 'text' | 'multiple_choice' | 'scale' | 'file_upload';
  question_text: string;
  options: any;
  order_index: number;
  is_required: boolean;
}

interface Questionnaire {
  id?: number;
  title: string;
  description: string;
  questions: Question[];
}

export default function QuestionnaireBuilderPage() {
  const [questionnaire, setQuestionnaire] = useState<Questionnaire>({
    title: '',
    description: '',
    questions: []
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [draggedItem, setDraggedItem] = useState<number | null>(null);
  const [previewMode, setPreviewMode] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const questionnaireId = searchParams.get('id');
  const programId = searchParams.get('programId');

  useEffect(() => {
    if (questionnaireId) {
      loadQuestionnaire();
    }
  }, [questionnaireId]);

  const loadQuestionnaire = async () => {
    if (!questionnaireId) return;
    
    setLoading(true);
    try {
      const data = await apiService.get(`/questions/questionnaires/${questionnaireId}`);
      setQuestionnaire({
        id: data.id,
        title: data.name,
        description: data.description || '',
        questions: (data.questions || []).map((q: any) => ({
          id: q.id,
          question_type: q.question_type,
          question_text: q.text, // Map backend 'text' to frontend 'question_text'
          text: q.text, // Also keep 'text' for API compatibility
          options: q.options || {},
          order_index: q.order_index,
          is_required: q.is_required,
          validation_rules: q.validation_rules || {},
          questionnaire_id: q.questionnaire_id
        }))
      });
    } catch (error: any) {
      console.error('Error loading questionnaire:', error);
    } finally {
      setLoading(false);
    }
  };

  const addQuestion = (type: Question['question_type']) => {
    if (questionnaire.questions.length >= 50) {
      alert('Maximum 50 questions allowed per questionnaire');
      return;
    }

    const newQuestion: Question = {
      question_type: type,
      question_text: '',
      text: '', // Also include 'text' for API compatibility
      options: getDefaultOptions(type),
      order_index: questionnaire.questions.length,
      is_required: false
    };

    setQuestionnaire(prev => ({
      ...prev,
      questions: [...prev.questions, newQuestion]
    }));
  };

  const getDefaultOptions = (type: Question['question_type']) => {
    switch (type) {
      case 'text':
        return { max_length: 500, multiline: false };
      case 'multiple_choice':
        return { 
          choices: ['Option 1', 'Option 2'],
          multiple_selection: false,
          randomize: false
        };
      case 'scale':
        return { min_value: 1, max_value: 10, step: 1 };
      case 'file_upload':
        return { max_size_mb: 10, allowed_extensions: ['.pdf'] };
      default:
        return {};
    }
  };

  const updateQuestion = (index: number, field: string, value: any) => {
    setQuestionnaire(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => {
        if (i === index) {
          const updated = { ...q, [field]: value };
          // Keep text fields in sync
          if (field === 'question_text') {
            updated.text = value;
          } else if (field === 'text') {
            updated.question_text = value;
          }
          return updated;
        }
        return q;
      })
    }));
  };

  const removeQuestion = (index: number) => {
    setQuestionnaire(prev => ({
      ...prev,
      questions: prev.questions
        .filter((_, i) => i !== index)
        .map((q, i) => ({ ...q, order_index: i }))
    }));
  };

  const moveQuestion = (fromIndex: number, toIndex: number) => {
    const questions = [...questionnaire.questions];
    const [movedQuestion] = questions.splice(fromIndex, 1);
    questions.splice(toIndex, 0, movedQuestion);
    
    setQuestionnaire(prev => ({
      ...prev,
      questions: questions.map((q, i) => ({ ...q, order_index: i }))
    }));
  };

  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedItem(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    if (draggedItem !== null && draggedItem !== dropIndex) {
      moveQuestion(draggedItem, dropIndex);
    }
    setDraggedItem(null);
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
  };

  const saveQuestionnaire = async () => {
    if (!questionnaire.title.trim()) {
      alert('Please enter a questionnaire title');
      return;
    }

    if (questionnaire.questions.length === 0) {
      alert('Please add at least one question');
      return;
    }

    setSaving(true);
    try {
      // Save questionnaire metadata first
      const questionnaireResult = await apiService.saveQuestionnaire({
        id: questionnaire.id,
        title: questionnaire.title,
        description: questionnaire.description
      });

      if (questionnaireResult.error) {
        throw new Error(questionnaireResult.error);
      }

      const savedQuestionnaire = questionnaireResult.data;
      const questionnaireId = savedQuestionnaire.id;

      // Save/update each question using the REAL questionnaire ID
      for (const question of questionnaire.questions) {
        if (question.id) {
          // Update existing question
          const updateResult = await apiService.updateQuestion(question.id, {
            ...question,
            questionnaire_id: questionnaireId
          });
          if (updateResult.error) {
            console.error('Error updating question:', updateResult.error);
            throw new Error(`Failed to update question: ${updateResult.error}`);
          }
        } else {
          // Create new question with the correct questionnaire ID
          const createResult = await apiService.createQuestion(questionnaireId, {
            ...question,
            text: question.text,
            order_index: question.order_index ?? questionnaire.questions.indexOf(question)
          });
          if (createResult.error) {
            console.error('Error creating question:', createResult.error);
            throw new Error(`Failed to create question: ${createResult.error}`);
          }
        }
      }

      alert('Questionnaire saved successfully!');
      
      // Redirect back to program-specific questionnaires if program context exists
      if (programId) {
        router.push(`/dashboard/programs/${programId}/questionnaires`);
      } else {
        // Fallback to program selection if no program context
        router.push('/dashboard/programs');
      }
    } catch (error) {
      console.error('Error saving questionnaire:', error);
      alert(`Error saving questionnaire: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link 
                href={programId ? `/dashboard/programs/${programId}/questionnaires` : "/dashboard/questionnaires"} 
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back to Questionnaires
              </Link>
              <h1 className="text-xl font-semibold text-gray-900">
                {questionnaireId ? 'Edit Questionnaire' : 'Create Questionnaire'}
              </h1>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPreviewMode(!previewMode)}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                {previewMode ? 'Edit Mode' : 'Preview Mode'}
              </button>
              <button
                onClick={saveQuestionnaire}
                disabled={saving}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                {saving ? 'Saving...' : 'Save Questionnaire'}
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Questionnaire Details */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Questionnaire Details</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Title</label>
                <input
                  type="text"
                  value={questionnaire.title}
                  onChange={(e) => setQuestionnaire(prev => ({ ...prev, title: e.target.value }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter questionnaire title"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  value={questionnaire.description}
                  onChange={(e) => setQuestionnaire(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter questionnaire description"
                />
              </div>
            </div>
          </div>

          {/* Question Builder */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium text-gray-900">
                {previewMode ? 'Questionnaire Preview' : `Questions (${questionnaire.questions.length}/50)`}
              </h2>
              {!previewMode && questionnaire.questions.length >= 50 && (
                <span className="text-sm text-red-600">Maximum questions reached</span>
              )}
            </div>

            {/* Add Question Buttons - Only show in edit mode */}
            {!previewMode && (
              <div className="mb-6">
                <p className="text-sm text-gray-600 mb-3">Add a new question:</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <button
                    onClick={() => addQuestion('text')}
                    disabled={questionnaire.questions.length >= 50}
                    className="p-3 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-1">📝</div>
                      <div className="text-sm font-medium">Text</div>
                    </div>
                  </button>
                  <button
                    onClick={() => addQuestion('multiple_choice')}
                    disabled={questionnaire.questions.length >= 50}
                    className="p-3 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-1">☑️</div>
                      <div className="text-sm font-medium">Multiple Choice</div>
                    </div>
                  </button>
                  <button
                    onClick={() => addQuestion('scale')}
                    disabled={questionnaire.questions.length >= 50}
                    className="p-3 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-1">📊</div>
                      <div className="text-sm font-medium">Scale</div>
                    </div>
                  </button>
                  <button
                    onClick={() => addQuestion('file_upload')}
                    disabled={questionnaire.questions.length >= 50}
                    className="p-3 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-1">📎</div>
                      <div className="text-sm font-medium">File Upload</div>
                    </div>
                  </button>
                </div>
              </div>
            )}

            {/* Questions List */}
            <div className="space-y-4">
              {questionnaire.questions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>
                    {previewMode 
                      ? 'No questions to preview. Switch to edit mode to add questions.' 
                      : 'No questions added yet. Use the buttons above to add your first question.'
                    }
                  </p>
                </div>
              ) : previewMode ? (
                // Preview Mode - Show questions as they would appear to users
                <div className="space-y-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{questionnaire.title || 'Untitled Questionnaire'}</h3>
                    {questionnaire.description && (
                      <p className="text-gray-600">{questionnaire.description}</p>
                    )}
                  </div>
                  {questionnaire.questions.map((question, index) => (
                    <QuestionPreview 
                      key={index} 
                      question={question} 
                      questionNumber={index + 1} 
                    />
                  ))}
                </div>
              ) : (
                // Edit Mode - Show questions with editing controls
                questionnaire.questions.map((question, index) => (
                  <div 
                    key={index} 
                    className={`border border-gray-200 rounded-lg p-4 ${
                      draggedItem === index ? 'opacity-50' : ''
                    }`}
                    draggable
                    onDragStart={(e) => handleDragStart(e, index)}
                    onDragOver={handleDragOver}
                    onDrop={(e) => handleDrop(e, index)}
                    onDragEnd={handleDragEnd}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="cursor-move text-gray-400 hover:text-gray-600" title="Drag to reorder">
                          ⋮⋮
                        </span>
                        <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                          {question.question_type.replace('_', ' ')}
                        </span>
                        <span className="text-sm text-gray-500">Question {index + 1}</span>
                      </div>
                      <div className="flex space-x-2">
                        {index > 0 && (
                          <button
                            onClick={() => moveQuestion(index, index - 1)}
                            className="text-gray-400 hover:text-gray-600"
                            title="Move up"
                          >
                            ↑
                          </button>
                        )}
                        {index < questionnaire.questions.length - 1 && (
                          <button
                            onClick={() => moveQuestion(index, index + 1)}
                            className="text-gray-400 hover:text-gray-600"
                            title="Move down"
                          >
                            ↓
                          </button>
                        )}
                        <button
                          onClick={() => removeQuestion(index)}
                          className="text-red-400 hover:text-red-600"
                          title="Delete question"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Question Text</label>
                        <input
                          type="text"
                          value={question.question_text}
                          onChange={(e) => updateQuestion(index, 'question_text', e.target.value)}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Enter your question"
                        />
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id={`required-${index}`}
                          checked={question.is_required}
                          onChange={(e) => updateQuestion(index, 'is_required', e.target.checked)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor={`required-${index}`} className="ml-2 block text-sm text-gray-900">
                          Required question
                        </label>
                      </div>

                      {/* Question-specific options */}
                      {question.question_type === 'text' && (
                        <TextQuestionBuilder
                          options={question.options}
                          onChange={(options) => updateQuestion(index, 'options', options)}
                        />
                      )}
                      {question.question_type === 'multiple_choice' && (
                        <MultipleChoiceQuestionBuilder
                          options={question.options}
                          onChange={(options) => updateQuestion(index, 'options', options)}
                        />
                      )}
                      {question.question_type === 'scale' && (
                        <ScaleQuestionBuilder
                          options={question.options}
                          onChange={(options) => updateQuestion(index, 'options', options)}
                        />
                      )}
                      {question.question_type === 'file_upload' && (
                        <FileUploadQuestionBuilder
                          options={question.options}
                          onChange={(options) => updateQuestion(index, 'options', options)}
                        />
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}