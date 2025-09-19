import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import type { FileRejection } from 'react-dropzone';

interface FileUploadZoneProps {
  onFileSelect: (file: File) => void;
  accept: Record<string, string[]>;
  maxSize?: number;
  currentFile?: File;
  preview?: string;
  children: React.ReactNode;
  className?: string;
}

export default function FileUploadZone({
  onFileSelect,
  accept,
  maxSize = 10 * 1024 * 1024, 
  currentFile,
  preview,
  children,
  className = '',
}: FileUploadZoneProps) {
  const [error, setError] = useState<string>('');

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
      setError('');
      
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors.some((e) => e.code === 'file-too-large')) {
          setError('File is too large. Maximum size is 10MB.');
        } else if (rejection.errors.some((e) => e.code === 'file-invalid-type')) {
          setError('Invalid file type. Please check supported formats.');
        } else {
          setError('Error uploading file. Please try again.');
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${className}
        `}
      >
        <input {...getInputProps()} />
        
        {preview ? (
          <div className="space-y-4">
            <img
              src={preview}
              alt="Preview"
              className="max-w-full max-h-48 mx-auto rounded-lg shadow-sm"
            />
            <p className="text-sm text-gray-600">
              {currentFile?.name}
            </p>
            <p className="text-xs text-gray-500">
              Click or drag to replace
            </p>
          </div>
        ) : currentFile ? (
          <div className="space-y-2">
            <div className="text-green-600">
              <svg className="w-8 h-8 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="text-sm font-medium text-gray-900">
              {currentFile.name}
            </p>
            <p className="text-xs text-gray-500">
              Click or drag to replace
            </p>
          </div>
        ) : (
          children
        )}
      </div>
      
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
