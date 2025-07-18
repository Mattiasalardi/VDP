interface Question {
  id?: number;
  question_type: 'text' | 'multiple_choice' | 'scale' | 'file_upload';
  question_text: string;
  options: any;
  order_index: number;
  is_required: boolean;
}

interface QuestionPreviewProps {
  question: Question;
  questionNumber: number;
}

export default function QuestionPreview({ question, questionNumber }: QuestionPreviewProps) {
  const renderQuestionInput = () => {
    switch (question.question_type) {
      case 'text':
        return question.options.multiline ? (
          <textarea
            placeholder={question.options.placeholder || 'Enter your answer...'}
            maxLength={question.options.max_length || 500}
            rows={4}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled
          />
        ) : (
          <input
            type="text"
            placeholder={question.options.placeholder || 'Enter your answer...'}
            maxLength={question.options.max_length || 500}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled
          />
        );

      case 'multiple_choice':
        const inputType = question.options.multiple_selection ? 'checkbox' : 'radio';
        return (
          <div className="space-y-2">
            {(question.options.choices || []).map((choice: string, index: number) => (
              <label key={index} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type={inputType}
                  name={`question-${questionNumber}`}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  disabled
                />
                <span className="text-gray-700">{choice}</span>
              </label>
            ))}
            {question.options.other_option && (
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type={inputType}
                  name={`question-${questionNumber}`}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  disabled
                />
                <span className="text-gray-700">Other:</span>
                <input
                  type="text"
                  placeholder="Please specify..."
                  className="ml-2 border border-gray-300 rounded px-2 py-1 text-sm"
                  disabled
                />
              </label>
            )}
          </div>
        );

      case 'scale':
        const min = question.options.min_value || 1;
        const max = question.options.max_value || 10;
        const step = question.options.step || 1;
        const values = [];
        for (let i = min; i <= max; i += step) {
          values.push(i);
        }
        
        return (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">
                {question.options.min_label || min}
              </span>
              <span className="text-sm text-gray-600">
                {question.options.max_label || max}
              </span>
            </div>
            <div className="flex justify-between">
              {values.map((value) => (
                <label key={value} className="flex flex-col items-center cursor-pointer">
                  <input
                    type="radio"
                    name={`question-${questionNumber}`}
                    value={value}
                    className="h-4 w-4 text-blue-600 border-gray-300"
                    disabled
                  />
                  <span className="text-sm text-gray-600 mt-1">{value}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'file_upload':
        return (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <div className="text-gray-400 mb-2">
              <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p className="text-gray-600">
              {question.options.multiple_files ? 'Drop files here or click to upload' : 'Drop file here or click to upload'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Max size: {question.options.max_size_mb || 10}MB • 
              Types: {(question.options.allowed_extensions || ['.pdf']).join(', ')}
            </p>
          </div>
        );

      default:
        return <div className="text-gray-500">Preview not available for this question type</div>;
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-sm font-medium text-gray-500">Question {questionNumber}</span>
          {question.is_required && (
            <span className="text-red-500 text-sm">*</span>
          )}
        </div>
        <h3 className="text-lg font-medium text-gray-900">
          {question.question_text || 'Untitled Question'}
        </h3>
      </div>
      
      <div className="mb-4">
        {renderQuestionInput()}
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>Type: {question.question_type.replace('_', ' ')}</span>
        {question.is_required && <span>Required</span>}
      </div>
    </div>
  );
}