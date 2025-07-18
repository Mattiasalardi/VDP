interface MultipleChoiceQuestionBuilderProps {
  options: {
    choices?: string[];
    multiple_selection?: boolean;
    randomize?: boolean;
    other_option?: boolean;
  };
  onChange: (options: any) => void;
}

export default function MultipleChoiceQuestionBuilder({ 
  options, 
  onChange 
}: MultipleChoiceQuestionBuilderProps) {
  const choices = options.choices || ['Option 1', 'Option 2'];
  
  const updateOption = (key: string, value: any) => {
    onChange({ ...options, [key]: value });
  };

  const updateChoice = (index: number, value: string) => {
    const newChoices = [...choices];
    newChoices[index] = value;
    updateOption('choices', newChoices);
  };

  const addChoice = () => {
    if (choices.length < 20) {
      updateOption('choices', [...choices, `Option ${choices.length + 1}`]);
    }
  };

  const removeChoice = (index: number) => {
    if (choices.length > 2) {
      const newChoices = choices.filter((_, i) => i !== index);
      updateOption('choices', newChoices);
    }
  };

  return (
    <div className="space-y-3 p-3 bg-gray-50 rounded">
      <h4 className="text-sm font-medium text-gray-700">Multiple Choice Options</h4>
      
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm text-gray-600">Choices ({choices.length}/20)</label>
          <button
            onClick={addChoice}
            disabled={choices.length >= 20}
            className="text-xs bg-blue-600 text-white px-2 py-1 rounded disabled:bg-gray-400"
          >
            Add Choice
          </button>
        </div>
        
        <div className="space-y-2">
          {choices.map((choice, index) => (
            <div key={index} className="flex gap-2">
              <input
                type="text"
                value={choice}
                onChange={(e) => updateChoice(index, e.target.value)}
                className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
                placeholder={`Option ${index + 1}`}
              />
              {choices.length > 2 && (
                <button
                  onClick={() => removeChoice(index)}
                  className="text-red-600 hover:text-red-800 px-2"
                  title="Remove choice"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-col space-y-2">
        <div className="flex items-center">
          <input
            type="checkbox"
            id="multiple_selection"
            checked={options.multiple_selection || false}
            onChange={(e) => updateOption('multiple_selection', e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
          />
          <label htmlFor="multiple_selection" className="ml-2 text-sm text-gray-600">
            Allow multiple selections
          </label>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="randomize"
            checked={options.randomize || false}
            onChange={(e) => updateOption('randomize', e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
          />
          <label htmlFor="randomize" className="ml-2 text-sm text-gray-600">
            Randomize choice order
          </label>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="other_option"
            checked={options.other_option || false}
            onChange={(e) => updateOption('other_option', e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
          />
          <label htmlFor="other_option" className="ml-2 text-sm text-gray-600">
            Include "Other" option
          </label>
        </div>
      </div>
    </div>
  );
}