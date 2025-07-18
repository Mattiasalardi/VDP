interface TextQuestionBuilderProps {
  options: {
    max_length?: number;
    multiline?: boolean;
    placeholder?: string;
  };
  onChange: (options: any) => void;
}

export default function TextQuestionBuilder({ options, onChange }: TextQuestionBuilderProps) {
  const updateOption = (key: string, value: any) => {
    onChange({ ...options, [key]: value });
  };

  return (
    <div className="space-y-3 p-3 bg-gray-50 rounded">
      <h4 className="text-sm font-medium text-gray-700">Text Question Options</h4>
      
      <div>
        <label className="block text-sm text-gray-600 mb-1">Maximum Length</label>
        <input
          type="number"
          value={options.max_length || 500}
          onChange={(e) => updateOption('max_length', parseInt(e.target.value) || 500)}
          min="1"
          max="10000"
          className="w-32 border border-gray-300 rounded px-2 py-1 text-sm"
        />
        <span className="text-xs text-gray-500 ml-2">characters</span>
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-1">Placeholder Text</label>
        <input
          type="text"
          value={options.placeholder || ''}
          onChange={(e) => updateOption('placeholder', e.target.value)}
          className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          placeholder="Enter placeholder text..."
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="multiline"
          checked={options.multiline || false}
          onChange={(e) => updateOption('multiline', e.target.checked)}
          className="h-4 w-4 text-blue-600 border-gray-300 rounded"
        />
        <label htmlFor="multiline" className="ml-2 text-sm text-gray-600">
          Allow multiple lines (textarea)
        </label>
      </div>
    </div>
  );
}