import { Plus } from "lucide-react";

interface AddPromptCardProps {
  onClick: () => void;
}

export function AddPromptCard({ onClick }: AddPromptCardProps) {
  return (
    <button
      onClick={onClick}
      className="group relative flex flex-col items-center justify-center h-full min-h-[240px] w-full
                 rounded-2xl border-2 border-dashed border-white/20 bg-white/5 
                 backdrop-blur-sm transition-all duration-300 
                 hover:bg-white/10 hover:border-blue-400/50 hover:scale-[1.02] hover:shadow-lg"
    >
      {/* Icon Circle */}
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white/5 border border-white/10 transition-colors group-hover:bg-blue-500/20 group-hover:border-blue-400/30">
        <Plus
          size={32}
          className="text-white/40 transition-colors group-hover:text-blue-200"
        />
      </div>

      {/* Text */}
      <span className="text-lg font-bold text-white/40 transition-colors group-hover:text-white">
        Create New Prompt
      </span>
      <span className="mt-1 text-xs text-white/30 group-hover:text-white/60">
        Click to configure
      </span>
    </button>
  );
}
