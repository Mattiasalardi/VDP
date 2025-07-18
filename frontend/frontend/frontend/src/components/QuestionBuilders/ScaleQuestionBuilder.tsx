interface ScaleQuestionBuilderProps {
  options: {
    min_value?: number;
    max_value?: number;
    step?: number;
    min_label?: string;
    max_label?: string;
  };
  onChange: (options: any) => void;
}

export default function ScaleQuestionBuilder({ options, onChange }: ScaleQuestionBuilderProps) {
  const updateOption = (key: string, value: any) => {
    onChange({ ...options, [key]: value });
  };

  return (
    <div className="space-y-3 p-3 bg-gray-50 rounded">
      <h4 className="text-sm font-medium text-gray-700">Scale Question Options</h4>
      
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="block text-sm text-gray-600 mb-1">Minimum Value</label>
          <input
            type="number"
            value={options.min_value || 1}
            onChange={(e) => updateOption('min_value', parseInt(e.target.value) || 1)}
            min="0"
            max="9"
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">Maximum Value</label>
          <input
            type="number"
            value={options.max_value || 10}
            onChange={(e) => updateOption('max_value', parseInt(e.target.value) || 10)}
            min="2"
            max="100"
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">Step</label>
          <input
            type="number"
            value={options.step || 1}
            onChange={(e) => updateOption('step', parseInt(e.target.value) || 1)}
            min="1"
            max="10"
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm text-gray-600 mb-1">
            Label for {options.min_value || 1} (optional)
          </label>
          <input
            type="text"
            value={options.min_label || ''}
            onChange={(e) => updateOption('min_label', e.target.value)}
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
            placeholder="e.g. Strongly Disagree"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">
            Label for {options.max_value || 10} (optional)
          </label>
          <input
            type="text"
            value={options.max_label || ''}
            onChange={(e) => updateOption('max_label', e.target.value)}
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
            placeholder="e.g. Strongly Agree"
          />
        </div>
      </div>

      <div className="p-2 bg-white border rounded text-sm">
        <div className="text-gray-600 mb-1">Preview:</div>
        <div className="flex justify-between items-center">
          <span className="text-xs">{options.min_label || options.min_value || 1}</span>
          <div className="flex space-x-1">
            {Array.from({ 
              length: Math.floor(((options.max_value || 10) - (options.min_value || 1)) / (options.step || 1)) + 1 
            }).map((_, i) => (
              <div key={i} className="w-8 h-8 border border-gray-300 rounded flex items-center justify-center text-xs">
                {(options.min_value || 1) + i * (options.step || 1)}
              </div>
            ))}
          </div>
          <span className="text-xs">{options.max_label || options.max_value || 10}</span>
        </div>
      </div>
    </div>
  );
}