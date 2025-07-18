interface FileUploadQuestionBuilderProps {
  options: {
    max_size_mb?: number;
    allowed_extensions?: string[];
    multiple_files?: boolean;
  };
  onChange: (options: any) => void;
}

export default function FileUploadQuestionBuilder({ 
  options, 
  onChange 
}: FileUploadQuestionBuilderProps) {
  const updateOption = (key: string, value: any) => {
    onChange({ ...options, [key]: value });
  };

  const extensionOptions = ['.pdf', '.doc', '.docx', '.txt', '.png', '.jpg', '.jpeg'];

  const toggleExtension = (ext: string) => {
    const current = options.allowed_extensions || ['.pdf'];
    if (current.includes(ext)) {
      updateOption('allowed_extensions', current.filter(e => e !== ext));
    } else {
      updateOption('allowed_extensions', [...current, ext]);
    }
  };

  return (
    <div className="space-y-3 p-3 bg-gray-50 rounded">
      <h4 className="text-sm font-medium text-gray-700">File Upload Options</h4>
      
      <div>
        <label className="block text-sm text-gray-600 mb-1">Maximum File Size</label>
        <div className="flex items-center gap-2">
          <input
            type="number"
            value={options.max_size_mb || 10}
            onChange={(e) => updateOption('max_size_mb', parseInt(e.target.value) || 10)}
            min="1"
            max="100"
            className="w-24 border border-gray-300 rounded px-2 py-1 text-sm"
          />
          <span className="text-sm text-gray-600">MB</span>
        </div>
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-2">Allowed File Types</label>
        <div className="grid grid-cols-3 gap-2">
          {extensionOptions.map((ext) => (
            <div key={ext} className="flex items-center">
              <input
                type="checkbox"
                id={`ext-${ext}`}
                checked={(options.allowed_extensions || ['.pdf']).includes(ext)}
                onChange={() => toggleExtension(ext)}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded"
              />
              <label htmlFor={`ext-${ext}`} className="ml-2 text-sm text-gray-600">
                {ext}
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="multiple_files"
          checked={options.multiple_files || false}
          onChange={(e) => updateOption('multiple_files', e.target.checked)}
          className="h-4 w-4 text-blue-600 border-gray-300 rounded"
        />
        <label htmlFor="multiple_files" className="ml-2 text-sm text-gray-600">
          Allow multiple file uploads
        </label>
      </div>

      <div className="p-2 bg-white border rounded text-sm">
        <div className="text-gray-600 mb-1">Settings Summary:</div>
        <ul className="text-xs space-y-1">
          <li>Max size: {options.max_size_mb || 10} MB</li>
          <li>Types: {(options.allowed_extensions || ['.pdf']).join(', ')}</li>
          <li>Multiple files: {options.multiple_files ? 'Yes' : 'No'}</li>
        </ul>
      </div>
    </div>
  );
}