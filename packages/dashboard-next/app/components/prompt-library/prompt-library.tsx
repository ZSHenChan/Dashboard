"use client";
import { useEffect, useState } from "react";
import {
  FileText,
  Image as ImageIcon,
  Mic,
  Settings2,
  Maximize2,
  Search,
  Loader2,
  Box,
  Plus,
  File,
} from "lucide-react";
import { PromptRunnerModal } from "./prompt-runner-modal";
import { AddPromptCard } from "./add-prompt-card";
import { PromptConfig } from "./prompt-types";
import { AVAILABLE_MODELS } from "./prompt-config-sidebar";
import { Helix } from "ldrs/react";
import "ldrs/react/Helix.css";

const DEMO_PROMPTS: PromptConfig[] = [
  {
    id: "demo_3314",
    title: "Demo Prompt: Tailor Resume",
    summary: "Personal coach to customize your resume based on job role description",
    inputs: ["text", "file"],
    systemPrompt: `I am going to upload my resume and list out the job description posted by a company. I need you to:

1. Advise if my experiences and skills really fit the job role. Highlight the technical skills required by the role.

2. Clearly point out which part of my resume needed changes (for me to easily find out the part to edit my document).

3. Customize my resume to fit the job requirements and show the final result.`,
    addSysPrompt: ["skip_intro"],
    model: AVAILABLE_MODELS[0].label,
    persistInputs: [],
  },
];
// --- Mock Data ---
const EMPTY_TEMPLATE: PromptConfig = {
  id: "new", // distinct ID we can check later
  title: "New Prompt",
  summary: "Describe what this prompt does...",
  inputs: ["text"],
  systemPrompt: "You are a helpful AI assistant.",
  addSysPrompt: [],
  model: AVAILABLE_MODELS[0].label,
  persistInputs: [],
};

// --- Main Component ---

export function PromptLibrary() {
  const [selectedPrompt, setSelectedPrompt] = useState<PromptConfig | null>(null);
  const [prompts, setPrompts] = useState<PromptConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const loadPrompts = () => {
    fetch("/api/prompts")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data) && data.length != 0) setPrompts(data);
        else setPrompts(DEMO_PROMPTS);
        setIsLoading(false);
      })
      .catch(() => {
        setIsLoading(false);
        setPrompts(DEMO_PROMPTS);
      });
  };

  const fetchPrompts = () => {
    setIsLoading(true);
    loadPrompts();
  };

  const updatePromptsLocally = (prompt: PromptConfig, update: boolean) => {
    if (update) setPrompts((prev) => [prompt, ...prev.filter((p) => p.id != prompt.id)]);
    else setPrompts((prev) => [...prev.filter((p) => p.id != prompt.id)]);
  };

  useEffect(() => {
    loadPrompts();
  }, []);

  // Filter Logic
  const filteredPrompts = prompts.filter((prompt) => {
    const query = searchQuery.toLowerCase();
    return prompt.title.toLowerCase().includes(query) || prompt.summary.toLowerCase().includes(query);
  });

  const handleCreateNew = () => {
    // Open the modal with the empty template
    setSelectedPrompt(EMPTY_TEMPLATE);
  };

  if (isLoading) {
    return (
      <div className="w-full h-[60vh] flex flex-col items-center justify-center text-white/50">
        <Loader2 className="animate-spin mb-4" size={32} />
        <p>Loading your library...</p>
      </div>
    );
  }

  if (prompts.length === 0) {
    return (
      <div className="w-full h-[70vh] flex flex-col items-center justify-center p-6 text-center">
        <div className="p-6 rounded-full bg-white/5 border border-white/10 mb-6 shadow-[0_0_30px_rgba(255,255,255,0.05)]">
          <Box size={48} className="text-white/40" />
        </div>

        <h2 className="text-3xl font-bold text-white mb-3">No prompts created yet</h2>
        <p className="text-white/60 max-w-md mb-8 leading-relaxed">
          Your library is empty. Create your first reusable prompt template to start streamlining your AI workflow.
        </p>

        <button
          onClick={handleCreateNew}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold shadow-lg shadow-blue-500/20 transition-all hover:scale-105"
        >
          <Plus size={20} /> Create New Prompt
        </button>

        {/* Render Modal if they click create */}
        {selectedPrompt && <PromptRunnerModal prompt={selectedPrompt} onClose={() => setSelectedPrompt(null)} />}
      </div>
    );
  }

  return (
    <div className="w-full max-w-5xl mx-auto p-6">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
        <h2 className="text-3xl font-bold text-white/90 drop-shadow-md flex items-center gap-3">
          Prompt Library <Helix size="24" speed="4.0" color="white" />
        </h2>

        {/* Search Bar */}
        <div className="relative w-full md:w-96 group">
          <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-white/50 group-focus-within:text-blue-400 transition-colors" />
          </div>
          <input
            type="text"
            placeholder="Search prompts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder-white/40 backdrop-blur-sm transition-all focus:bg-black/40 focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 focus:outline-none"
          />
        </div>
      </div>

      {/* Grid Layout */}
      {filteredPrompts.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <AddPromptCard onClick={handleCreateNew} />
          {filteredPrompts.map((prompt) => (
            <button
              key={prompt.id}
              onClick={() => setSelectedPrompt(prompt)}
              className="group relative flex flex-col text-left h-full overflow-hidden rounded-2xl border border-white/20 bg-white/10 p-6 shadow-lg backdrop-blur-md transition-all hover:scale-[1.02] hover:bg-white/20 hover:border-white/40"
            >
              {/* Header */}
              <div className="flex justify-between items-start w-full mb-4">
                <div className="p-3 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/10">
                  <Settings2 size={24} className="text-white/80" />
                </div>

                {/* Input Type Badges */}
                <div className="flex gap-1.5">
                  {prompt.inputs.map((type) => (
                    <div key={type} className="p-1.5 rounded-md bg-black/20 text-white/70" title={`Supports ${type}`}>
                      {type === "text" && <FileText size={14} />}
                      {type === "image" && <ImageIcon size={14} />}
                      {type === "audio" && <Mic size={14} />}
                      {type === "file" && <File size={14} />}
                    </div>
                  ))}
                </div>
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-200 transition-colors">
                {prompt.title}
              </h3>
              <p className="text-sm text-white/70 leading-relaxed">{prompt.summary}</p>

              {/* Hover Action Indicator */}
              <div className="mt-auto pt-6 flex items-center text-xs font-bold uppercase tracking-widest text-white/40 group-hover:text-white/90 transition-colors">
                Configure & Run <Maximize2 size={12} className="ml-2" />
              </div>
            </button>
          ))}
        </div>
      ) : (
        // Empty State
        <div className="flex flex-col items-center justify-center py-20 text-white/40">
          <Search size={48} className="mb-4 opacity-50" />
          <p className="text-lg font-medium">No prompts found matching &quot;{searchQuery}&quot;</p>
          <button
            onClick={() => setSearchQuery("")}
            className="mt-4 text-sm text-blue-300 hover:text-blue-200 underline"
          >
            Clear search
          </button>
        </div>
      )}

      {/* Modal Overlay */}
      {selectedPrompt && (
        <PromptRunnerModal
          prompt={selectedPrompt}
          onClose={() => setSelectedPrompt(null)}
          onSaveSuccess={updatePromptsLocally}
        />
      )}
    </div>
  );
}
