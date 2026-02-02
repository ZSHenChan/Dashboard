"use client";
import { useState } from "react";
import { X, Loader2, Save, Trash2 } from "lucide-react";
import { PromptConfigSidebar } from "./prompt-config-sidebar";
import { PromptConfig } from "./prompt-types";
import { PromptOutput } from "./modal-textarea";
import { PromptInputArea } from "./input";

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
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Saving State
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

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
            <PromptOutput isLoading={isLoading} response={response} />

            {/* Input Area */}
            <PromptInputArea
              value={userInput}
              onChange={setUserInput}
              selectedImage={selectedImage}
              onImageSelect={setSelectedImage}
              onRun={handleRun}
              isLoading={isLoading}
              supportedInputs={prompt.inputs}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
