"use client";

import { useRef } from "react";
import { Image as ImageIcon, X, Play } from "lucide-react";

interface PromptInputAreaProps {
  value: string;
  onChange: (value: string) => void;
  selectedImage: {
    data: string;
    mimeType: string;
    preview: string;
  } | null;
  onImageSelect: (
    image: {
      data: string;
      mimeType: string;
      preview: string;
    } | null,
  ) => void;
  onRun: () => void;
  isLoading: boolean;
  supportedInputs: string[];
}

export function PromptInputArea({
  value,
  onChange,
  selectedImage,
  onImageSelect,
  onRun,
  isLoading,
  supportedInputs,
}: PromptInputAreaProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDoubleClickPaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      onChange(value + text);
    } catch (err) {
      console.error("Failed to read clipboard:", err);
      alert("Please allow clipboard access to use double-click paste.");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && e.shiftKey) {
      e.preventDefault();
      if (value.trim() !== "") onRun();
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      // Strip metadata prefix for API compatibility
      const base64Data = base64String.split(",")[1];

      onImageSelect({
        data: base64Data,
        mimeType: file.type,
        preview: base64String,
      });
    };
    reader.readAsDataURL(file);
  };

  const handleClearImage = () => {
    onImageSelect(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="p-4 bg-black/20">
      <div className="relative">
        {/* Image Preview - check 'image' support as per original code */}
        {supportedInputs.includes("image") && selectedImage && (
          <div className="absolute bottom-16 left-0 mb-2 flex items-center gap-2 bg-white/10 backdrop-blur-md px-3 py-2 rounded-lg border border-white/20 animate-in slide-in-from-bottom-2">
            <img
              src={selectedImage.preview}
              alt="Upload preview"
              className="w-8 h-8 rounded object-cover border border-white/30"
            />
            <span className="text-xs text-white/80">Image attached</span>
            <button
              onClick={handleClearImage}
              className="ml-2 hover:text-red-400 text-white/50 transition"
            >
              <X size={14} />
            </button>
          </div>
        )}

        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onDoubleClick={handleDoubleClickPaste}
          onKeyDown={handleKeyDown}
          placeholder={"Enter your prompt here, or DOUBLE click to paste"}
          className="w-full h-24 bg-white/5 border border-white/10 rounded-xl p-4 pr-32 text-white placeholder-white/30 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
        />

        {/* Action Bar inside Textarea */}
        <div className="absolute bottom-3 right-3 flex items-center gap-2">
          {/* Upload Button - check 'file' support as per original code */}
          {supportedInputs.includes("file") && (
            <>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept="image/*"
                onChange={handleImageUpload}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className={`p-2 rounded-lg transition ${
                  selectedImage
                    ? "bg-blue-500/20 text-blue-300 ring-1 ring-blue-500/50"
                    : "bg-white/10 hover:bg-white/20 text-white/70 hover:text-white"
                }`}
                title="Upload Image"
              >
                <ImageIcon size={18} />
              </button>
            </>
          )}

          <button
            onClick={onRun}
            disabled={isLoading || !value.trim()}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Running..." : "Run"}{" "}
            <Play size={14} fill="currentColor" />
          </button>
        </div>
      </div>
    </div>
  );
}
