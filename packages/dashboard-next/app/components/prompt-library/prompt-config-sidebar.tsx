"use client";
import {
  ChevronLeft,
  ChevronRight,
  File,
  FileText,
  ImageIcon,
  Mic,
  Settings2,
} from "lucide-react";
import { InputType, PromptConfig } from "./prompt-types";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  config: PromptConfig;
  onChange: (key: keyof PromptConfig, value: any) => void;
}

interface GEMINI_MODEL_TEMPLATE {
  name: string;
  model: string;
}

export const AVAILABLE_MODEL: GEMINI_MODEL_TEMPLATE[] = [
  { name: "Gemini 3 Pro Preview", model: "gemini-3-pro-preview" },
  { name: "Gemini 3 Flash Preview", model: "gemini-3-flash-preview" },
  { name: "Gemini 2.5 Pro", model: "gemini-2.5-pro" },
  { name: "Gemini 2.5 Flash", model: "gemini-2.5-flash" },
];

export function PromptConfigSidebar({
  isOpen,
  onToggle,
  config,
  onChange,
}: SidebarProps) {
  // Helper to toggle input types (text/image/audio)
  const toggleInput = (type: InputType) => {
    const current = config.inputs;
    const updated = current.includes(type)
      ? current.filter((t) => t !== type)
      : [...current, type];
    onChange("inputs", updated);
  };

  return (
    <div
      className={`relative border-r border-white/10 bg-black/20 flex flex-col transition-all duration-300 ease-in-out ${
        isOpen ? "w-80 md:w-80 opacity-100" : "w-8 md:w-12 opacity-100" // w-12 allows space for the toggle button strip
      }`}
    >
      {/* Toggle Button (Always visible) */}
      <button
        onClick={onToggle}
        className={`absolute -right-3 top-4 z-20 p-1 bg-blue-600 rounded-full text-white shadow-lg hover:bg-blue-500 transition-colors border border-white/10 ${isOpen ? "" : ""}`}
        title={isOpen ? "Collapse Sidebar" : "Expand Sidebar"}
      >
        {isOpen ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
      </button>

      {/* Vertical Strip (Visible ONLY when collapsed) */}
      {!isOpen && (
        <div className="flex flex-col items-center pt-14 gap-4 opacity-50">
          <Settings2 size={20} className="text-white" />
          <div className="h-px w-4 bg-white/20" />
          {/* Mini indicators of what inputs are enabled */}
          {config.inputs.includes("text") && (
            <FileText size={16} className="text-blue-400" />
          )}
          {config.inputs.includes("image") && (
            <ImageIcon size={16} className="text-purple-400" />
          )}
          {config.inputs.includes("file") && (
            <File size={16} className="text-orange-400" />
          )}
        </div>
      )}

      {/* Main Content (Visible ONLY when open) */}
      <div
        className={`flex-1 overflow-y-auto custom-scrollbar p-5 space-y-5 transition-opacity duration-200 ${isOpen ? "opacity-100" : "opacity-0 hidden"}`}
      >
        {/* Title Input */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-white/50 mb-2">
            Title
          </label>
          <input
            type="text"
            value={config.title}
            onChange={(e) => onChange("title", e.target.value)}
            className="w-full bg-black/30 border border-white/10 rounded-lg p-2 text-white font-bold focus:ring-1 focus:ring-blue-500 outline-none transition-all"
            placeholder="e.g. Resume Fixer"
          />
        </div>

        {/* Summary Input */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-white/50 mb-2">
            Summary
          </label>
          <textarea
            value={config.summary}
            onChange={(e) => onChange("summary", e.target.value)}
            className="w-full bg-black/30 border border-white/10 rounded-lg p-2 text-sm text-white/80 resize-none h-20 focus:ring-1 focus:ring-blue-500 outline-none transition-all"
            placeholder="Short description..."
          />
        </div>

        {/* Supported Inputs Selector */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-white/50 mb-2">
            Supported Inputs
          </label>
          <div className="flex gap-2">
            <InputToggle
              label="Text"
              icon={<FileText size={14} />}
              active={config.inputs.includes("text")}
              onClick={() => toggleInput("text")}
              color="blue"
            />
            <InputToggle
              label="Image"
              icon={<ImageIcon size={14} />}
              active={config.inputs.includes("image")}
              onClick={() => toggleInput("image")}
              color="purple"
            />
            {/* <InputToggle
              label="Audio"
              icon={<Mic size={14} />}
              active={config.inputs.includes("audio")}
              onClick={() => toggleInput("audio")}
              color="orange"
            /> */}
            <InputToggle
              label="File"
              icon={<File size={14} />}
              active={config.inputs.includes("file")}
              onClick={() => toggleInput("file")}
              color="orange"
            />
          </div>
        </div>

        <div className="h-px bg-white/10" />

        {/* System Prompt Input */}
        <div className="flex-1 flex flex-col">
          <label className="block text-xs font-semibold uppercase tracking-wider text-blue-400 mb-2">
            System Instructions
          </label>
          <textarea
            value={config.systemPrompt}
            onChange={(e) => onChange("systemPrompt", e.target.value)}
            className="w-full h-64 bg-black/30 border border-white/10 rounded-lg p-3 text-sm text-white/90 placeholder-white/30 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none font-mono transition-all"
            placeholder="You are a helpful assistant..."
          />
        </div>

        {/* Model Config */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-white/50 mb-2">
            Model
          </label>
          <select
            value={config.model}
            onChange={(e) => onChange("model", e.target.value)}
            className="w-full bg-black/30 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none"
          >
            {AVAILABLE_MODEL.map((model) => (
              <option key={model.model} value={model.model}>
                {model.name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

// Sub-component for buttons to keep JSX clean
function InputToggle({ label, icon, active, onClick, color }: any) {
  const colorClasses: any = {
    blue: "border-blue-500 shadow-blue-500/20",
    purple: "border-purple-500 shadow-purple-500/20",
    orange: "border-orange-500 shadow-orange-500/20",
    green: "border-green-500 shadow-green-500/20",
  };

  return (
    <button
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg border text-sm font-medium transition-all ${
        active
          ? `${colorClasses[color]} text-white shadow-lg`
          : "bg-black/30 border-white/10 text-white/50 hover:bg-white/5 hover:text-white"
      }`}
    >
      {icon} {label}
    </button>
  );
}
