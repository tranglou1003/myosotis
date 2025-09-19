import type { Components } from 'react-markdown';

export const chatMarkdownComponents: Components = {
  
  p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
  h1: ({ children }) => <h1 className="text-xl font-bold mb-3">{children}</h1>,
  h2: ({ children }) => <h2 className="text-lg font-bold mb-2">{children}</h2>,
  h3: ({ children }) => <h3 className="text-base font-bold mb-2">{children}</h3>,
  h4: ({ children }) => <h4 className="text-base font-semibold mb-2">{children}</h4>,
  h5: ({ children }) => <h5 className="text-sm font-semibold mb-2">{children}</h5>,
  h6: ({ children }) => <h6 className="text-sm font-semibold mb-2">{children}</h6>,
  ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
  li: ({ children }) => <li className="ml-2">{children}</li>,
  strong: ({ children }) => <strong className="font-bold">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  code: ({ children }) => (
    <code className="bg-white/20 text-white px-1 py-0.5 rounded text-sm font-mono">
      {children}
    </code>
  ),
  pre: ({ children }) => (
    <pre className="bg-white/20 text-white p-3 rounded-lg text-sm font-mono overflow-x-auto mb-3">
      {children}
    </pre>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-white/30 pl-4 italic mb-3">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="border-white/30 my-4" />,
  a: ({ href, children }) => (
    <a 
      href={href} 
      className="underline hover:no-underline" 
      target="_blank" 
      rel="noopener noreferrer"
    >
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto mb-3">
      <table className="min-w-full border-collapse border border-white/30">
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-white/10">{children}</thead>,
  tbody: ({ children }) => <tbody>{children}</tbody>,
  tr: ({ children }) => <tr className="border-b border-white/20">{children}</tr>,
  th: ({ children }) => (
    <th className="border border-white/30 px-3 py-2 text-left font-semibold">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="border border-white/30 px-3 py-2">
      {children}
    </td>
  ),
};
