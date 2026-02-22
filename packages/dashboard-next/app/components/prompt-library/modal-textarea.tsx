import { Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math"; // Parses math syntax
import rehypeKatex from "rehype-katex"; // Renders math syntax
import "katex/dist/katex.min.css"; // Required CSS for math styling
import { Helix } from "ldrs/react";
import "ldrs/react/Helix.css";

interface PromptOutputProps {
  isLoading: boolean;
  response: string;
}

export function PromptOutput({ isLoading, response }: PromptOutputProps) {
  return (
    <div className="flex-1 p-6 overflow-y-auto border-b border-white/10">
      {isLoading ? (
        <div className="h-full flex flex-col items-center justify-center text-white/20">
          <Helix size="48" speed="2.5" color="white" />
          <p className="mt-8">Generating content...</p>
        </div>
      ) : response ? (
        <article className="prose prose-invert prose-md max-w-none leading-relaxed ">
          <ReactMarkdown
            remarkPlugins={[remarkGfm, remarkMath]} // Added remarkMath here
            rehypePlugins={[rehypeKatex]} // Added rehypeKatex here
            components={{
              // Custom Table Styling
              table: ({ children }) => (
                <div className="overflow-x-auto my-4 border border-white/10 rounded-lg">
                  <table className="min-w-full divide-y divide-white/10 text-sm">{children}</table>
                </div>
              ),
              th: ({ children }) => (
                <th className="px-4 py-3 bg-white/5 text-left font-semibold text-white">{children}</th>
              ),
              td: ({ children }) => <td className="px-4 py-3 border-t border-white/5 text-gray-300">{children}</td>,
            }}
          >
            {response}
          </ReactMarkdown>
        </article>
      ) : (
        /* Empty State */
        <div className="h-full flex flex-col items-center justify-center text-white/20">
          <Sparkles size={48} className="mb-4 opacity-50" />
          <p>Ready to generate content...</p>
        </div>
      )}
    </div>
  );
}
