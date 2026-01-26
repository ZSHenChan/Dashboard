"use client";
import { useRef, useState } from "react";
import {
  Image as ImageIcon,
  X,
  Play,
  Sparkles,
  Loader2,
  Save,
  Trash2,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { PromptConfigSidebar } from "./prompt-config-sidebar";
import { PromptConfig } from "./prompt-types";
import { Helix } from "ldrs/react";
import "ldrs/react/Helix.css";

// Default values shown
<Helix size="45" speed="2.5" color="black" />;

export function PromptRunnerModal({
  prompt,
  onClose,
  onSaveSuccess,
}: {
  prompt: PromptConfig;
  onClose: () => void;
  onSaveSuccess?: () => void;
}) {
  // 1. Consolidated Config State
  const [config, setConfig] = useState<PromptConfig>({
    id: prompt.id,
    title: prompt.title,
    summary: prompt.summary,
    systemPrompt: prompt.systemPrompt,
    addSysPrompt: prompt.addSysPrompt,
    model: prompt.model,
    inputs: prompt.inputs || ["text"],
    persistInputs: prompt.persistInputs || [],
  });

  // 2. UI State
  const [isSidebarOpen, setIsSidebarOpen] = useState(
    prompt.id === "new" ? true : false,
  );

  // Execution State
  const [userInput, setUserInput] = useState("");
  const [selectedImage, setSelectedImage] = useState<{
    data: string;
    mimeType: string;
    preview: string;
  } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Saving State
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDoubleClickPaste = async () => {
    try {
      // 1. Read text from clipboard
      const text = await navigator.clipboard.readText();

      // 2. Update state (Append to existing text to prevent accidental overwrite)
      setUserInput((prev) => prev + text);

      // Optional: Visual feedback could go here (e.g. toast "Pasted!")
    } catch (err) {
      console.error("Failed to read clipboard:", err);
      alert("Please allow clipboard access to use double-click paste.");
    }
  };

  const handleConfigChange = (key: keyof PromptConfig, value: any) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const handleDelete = async () => {
    // 1. Safety Check
    if (!confirm("Are you sure you want to delete this prompt template?"))
      return;

    setIsDeleting(true);
    try {
      const res = await fetch(`/api/prompts/${prompt.id}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Failed to delete");

      // 2. Refresh & Close
      if (onSaveSuccess) onSaveSuccess();
      onClose();
    } catch (error) {
      console.error(error);
      alert("Error deleting prompt");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleSave = async () => {
    if (!config.title.trim()) {
      alert("Please enter a title");
      return;
    }

    if (config.inputs.length === 0) {
      alert("Please select at least one input type.");
      return;
    }

    setIsSaving(true);
    try {
      const method = prompt.id === "new" ? "POST" : "PUT"; // POST for new, PUT for update
      const url =
        prompt.id === "new" ? "/api/prompts" : `/api/prompts/${prompt.id}`;

      const res = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: config.title,
          summary: config.summary,
          systemPrompt: config.systemPrompt,
          addSysPrompt: config.addSysPrompt,
          model: config.model,
          inputs: config.inputs,
          persistInputs: config.persistInputs,
        }),
      });

      if (!res.ok) throw new Error("Failed to save");

      if (onSaveSuccess) onSaveSuccess();
    } catch (error) {
      console.error(error);
      alert("Error saving template");
    } finally {
      setIsSaving(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      // We need to strip the metadata prefix (e.g., "data:image/png;base64,") for the API
      const base64Data = base64String.split(",")[1];

      setSelectedImage({
        data: base64Data,
        mimeType: file.type,
        preview: base64String,
      });
    };
    reader.readAsDataURL(file);
  };

  const handleRun = async () => {
    if (!userInput.trim()) return;

    setIsLoading(true);
    setResponse("");

    const finalSysPrompt =
      config.systemPrompt +
      `\nAdditionally, in your response:\n-${config.addSysPrompt.join("\n-")}`;

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: config.model,
          systemPrompt: finalSysPrompt,
          userPrompt: userInput,
          image: selectedImage
            ? {
                data: selectedImage.data,
                mimeType: selectedImage.mimeType,
              }
            : undefined,
          config: {
            temperature: 0.7,
          },
        }),
      });

      if (!res.ok) throw new Error(res.statusText);
      if (!res.body) throw new Error("No response body");

      // --- STREAMING LOGIC START ---
      if (!config.persistInputs.includes("text")) setUserInput("");
      if (!config.persistInputs.includes("file")) setSelectedImage(null);
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;

        if (value) {
          const chunk = decoder.decode(value, { stream: true });

          // Update state with new chunk
          setResponse((prev) => prev + chunk);
        }
      }
      // --- STREAMING LOGIC END ---
    } catch (error) {
      console.error("Stream error:", error);
      setResponse("Error: Failed to generate response.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-100 flex items-center justify-center p-4 sm:p-8">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Modal Window */}
      <div className="relative w-full max-w-4xl h-[85vh] bg-[#0f1115]/90 border border-white/20 rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/5">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            {prompt.id === "new" ? "Create New Prompt" : prompt.title}
          </h3>

          <div className="flex items-center gap-2">
            {/* DELETE BUTTON (Only show if it's an existing prompt) */}
            {prompt.id !== "new" && (
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 border border-red-500/20 transition mr-2"
                title="Delete Prompt"
              >
                {isDeleting ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <Trash2 size={18} />
                )}
              </button>
            )}

            {/* SAVE BUTTON */}
            <button
              onClick={handleSave}
              // ... (rest of save button code)
              className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-green-600 hover:bg-green-500 text-white font-semibold text-sm transition disabled:opacity-50"
            >
              {isSaving ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Save size={16} />
              )}
              {prompt.id === "new" ? "Create & Save" : "Update"}
            </button>

            <div className="h-6 w-px bg-white/20 mx-2" />

            <button
              onClick={onClose}
              className="text-white/50 hover:text-white transition"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Body - Two Columns */}
        <div className="flex-1 flex overflow-hidden">
          {/* LEFT COL: Configuration */}
          <PromptConfigSidebar
            isOpen={isSidebarOpen}
            onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
            config={config}
            onChange={handleConfigChange}
          />

          {/* RIGHT COL: Execution */}
          <div className="flex-3 flex flex-col bg-linear-to-bl from-white/5 to-transparent min-w-0">
            {/* Output Area */}
            <div className="flex-1 p-6 overflow-y-auto border-b border-white/10">
              {isLoading ? (
                <div className="h-full flex flex-col items-center justify-center text-white/20">
                  <Helix size="48" speed="2.5" color="white" />
                  <p className="mt-8">Generating content...</p>
                </div>
              ) : response ? (
                <article className="prose prose-invert prose-sm max-w-none leading-relaxed">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // Custom Table Styling
                      table: ({ children }) => (
                        <div className="overflow-x-auto my-4 border border-white/10 rounded-lg">
                          <table className="min-w-full divide-y divide-white/10 text-sm">
                            {children}
                          </table>
                        </div>
                      ),
                      th: ({ children }) => (
                        <th className="px-4 py-3 bg-white/5 text-left font-semibold text-white">
                          {children}
                        </th>
                      ),
                      td: ({ children }) => (
                        <td className="px-4 py-3 border-t border-white/5 text-gray-300">
                          {children}
                        </td>
                      ),
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

            {/* Input Area */}
            <div className="p-4 bg-black/20">
              <div className="relative">
                {prompt.inputs.includes("image") && selectedImage && (
                  <div className="absolute bottom-16 left-0 mb-2 flex items-center gap-2 bg-white/10 backdrop-blur-md px-3 py-2 rounded-lg border border-white/20 animate-in slide-in-from-bottom-2">
                    <img
                      src={selectedImage.preview}
                      alt="Upload preview"
                      className="w-8 h-8 rounded object-cover border border-white/30"
                    />
                    <span className="text-xs text-white/80">
                      Image attached
                    </span>
                    <button
                      onClick={() => {
                        setSelectedImage(null);
                        if (fileInputRef.current)
                          fileInputRef.current.value = "";
                      }}
                      className="ml-2 hover:text-red-400 text-white/50 transition"
                    >
                      <X size={14} />
                    </button>
                  </div>
                )}

                <textarea
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onDoubleClick={handleDoubleClickPaste}
                  placeholder={
                    "Enter your prompt here, or DOUBLE click to paste"
                  }
                  className="w-full h-24 bg-white/5 border border-white/10 rounded-xl p-4 pr-32 text-white placeholder-white/30 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                />

                {/* Action Bar inside Textarea */}
                <div className="absolute bottom-3 right-3 flex items-center gap-2">
                  {/* Upload Buttons based on supported inputs */}

                  {prompt.inputs.includes("file") && (
                    <>
                      <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept="file"
                        onChange={handleImageUpload}
                      />
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className={`p-2 rounded-lg transition ${selectedImage ? "bg-blue-500/20 text-blue-300 ring-1 ring-blue-500/50" : "bg-white/10 hover:bg-white/20 text-white/70 hover:text-white"}`}
                        title="Upload Image"
                      >
                        <ImageIcon size={18} />
                      </button>
                    </>
                  )}

                  <button
                    onClick={handleRun}
                    disabled={isLoading || !userInput.trim()}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? "Running..." : "Run"}{" "}
                    <Play size={14} fill="currentColor" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
