"use client";
import { useState } from "react";
import {
  Pencil,
  Send,
  X,
  Plus,
  MessageSquare,
  ChevronLeft,
  Layers,
  Trash2,
} from "lucide-react";
import { DashboardCard, ReplyOption } from "./reply-types"; // Assuming your types are here

const getUrgencyColor = (urgency: string) => {
  switch (urgency?.toLowerCase()) {
    case "high":
    case "critical":
      return "bg-red-500 shadow-red-500/80";
    case "medium":
    case "moderate":
      return "bg-yellow-400 shadow-yellow-400/80";
    default:
      return "bg-emerald-400 shadow-emerald-400/80"; // Low/Normal
  }
};

export function EventCard({
  card,
  onAction,
}: {
  card: DashboardCard;
  onAction: any;
}) {
  const [mode, setMode] = useState<"initial" | "selecting" | "composing">(
    "initial",
  );

  // CHANGED: Now manages an array of strings instead of a single string
  const [draftMessages, setDraftMessages] = useState<string[]>([""]);

  // Helper to color-code sentiment options
  const getButtonColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "bg-green-500/20 hover:bg-green-500/40 text-green-100 border border-green-500/30";
      case "negative":
        return "bg-red-500/20 hover:bg-red-500/40 text-red-100 border border-red-500/30";
      default:
        return "bg-blue-500/20 hover:bg-blue-500/40 text-blue-100 border border-blue-500/30";
    }
  };

  // Pre-fill the list when editing an existing option
  const handleEditOption = (texts: string[]) => {
    setDraftMessages([...texts]); // Clone to avoid ref issues
    setMode("composing");
  };

  // Start with one empty bubble for custom reply
  const handleCustomReply = () => {
    setDraftMessages([""]);
    setMode("composing");
  };

  // Manage individual inputs in the list
  const updateDraftMessage = (index: number, val: string) => {
    const newMsgs = [...draftMessages];
    newMsgs[index] = val;
    setDraftMessages(newMsgs);
  };

  const addMessageBubble = () => {
    setDraftMessages([...draftMessages, ""]);
  };

  const removeMessageBubble = (index: number) => {
    // Prevent removing the last remaining bubble
    if (draftMessages.length === 1) {
      updateDraftMessage(0, "");
      return;
    }
    const newMsgs = draftMessages.filter((_, i) => i !== index);
    setDraftMessages(newMsgs);
  };

  const handleSendDraft = () => {
    // Filter out empty strings before sending
    const cleanMessages = draftMessages.filter((m) => m.trim() !== "");
    if (cleanMessages.length === 0) return;
    onAction(card, "reply", cleanMessages);
  };

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border border-white/30 bg-white/20 shadow-xl backdrop-blur-xl transition-all duration-300 ease-in-out ${
        mode !== "initial"
          ? "ring-2 ring-white/40 scale-[1.01]"
          : "hover:scale-[1.02]"
      }`}
    >
      <div className="p-6 relative z-10">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            {/* Header with Urgency Dot */}
            <div className="flex items-center gap-2.5 mb-2">
              <span
                className={`h-2.5 w-2.5 rounded-full shadow-[0_0_10px] ${getUrgencyColor(
                  card.urgency,
                )}`}
                title={`Urgency: ${card.urgency}`}
              />
              <h3 className="text-lg font-bold text-white drop-shadow-sm leading-none">
                {card.sender}
              </h3>
            </div>

            <p className="text-white/90 font-medium">{card.summary}</p>
          </div>

          {/* Cancel Button (Top Right) */}
          {mode !== "initial" && (
            <button
              onClick={() => setMode("initial")}
              className="text-white/50 hover:text-white transition p-1 -mt-1 -mr-1"
            >
              <X size={20} />
            </button>
          )}
        </div>

        {/* --- VIEW 1: Initial Buttons --- */}
        {mode === "initial" && (
          <div className="mt-4 flex gap-3 animate-in fade-in slide-in-from-top-2 duration-300">
            <button
              onClick={() => setMode("selecting")}
              className="flex items-center gap-2 rounded-xl bg-white/80 px-4 py-2 text-sm font-semibold text-blue-900 shadow-sm transition hover:bg-white"
            >
              <MessageSquare size={16} /> Reply
            </button>
            <button
              onClick={() => onAction(card, "ignore")}
              className="rounded-xl border border-white/30 bg-black/20 px-4 py-2 text-sm font-medium text-white transition hover:bg-black/30"
            >
              Ignore
            </button>
          </div>
        )}

        {/* --- VIEW 2: Selection Grid --- */}
        {mode === "selecting" && (
          <div className="mt-6 animate-in fade-in zoom-in-95 duration-300">
            <span className="text-xs font-semibold uppercase tracking-widest text-white/60 mb-3 block">
              Select or Edit Response
            </span>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {card.reply_options.map((option: ReplyOption, idx: number) => (
                <div
                  key={idx}
                  className={`group relative flex flex-col items-start p-3 rounded-lg border transition-all ${getButtonColor(option.sentiment)}`}
                >
                  <button
                    className="w-full text-left h-full"
                    onClick={() => onAction(card, "reply", option.text)}
                  >
                    <div className="flex justify-between w-full">
                      <span className="font-bold text-sm uppercase tracking-wider opacity-90">
                        {option.label}
                      </span>
                      {/* Multi-message indicator */}
                      {option.text.length > 1 && (
                        <span className="flex items-center gap-1 text-[10px] bg-white/20 px-1.5 rounded-md">
                          <Layers size={10} /> +{option.text.length - 1}
                        </span>
                      )}
                    </div>

                    {/* Only show preview of the FIRST message */}
                    <span className="block text-xs opacity-80 mt-1 line-clamp-2 pr-6">
                      &quot;{option.text[0]}&quot;
                    </span>
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditOption(option.text);
                    }}
                    className="absolute top-2 right-2 p-1.5 rounded-full bg-white/10 hover:bg-white/30 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Edit sequence"
                  >
                    <Pencil size={12} />
                  </button>
                </div>
              ))}

              <button
                onClick={handleCustomReply}
                className="flex flex-col items-center justify-center p-3 rounded-lg border border-dashed border-white/40 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition-all min-h-[80px]"
              >
                <Plus size={24} className="mb-1 opacity-70" />
                <span className="text-xs font-medium uppercase tracking-wider">
                  Custom
                </span>
              </button>
            </div>
          </div>
        )}

        {/* --- VIEW 3: Composing (Multi-Message) --- */}
        {mode === "composing" && (
          <div className="mt-6 animate-in fade-in slide-in-from-right-4 duration-300">
            <div className="flex items-center gap-2 mb-3 text-white/70">
              <button
                onClick={() => setMode("selecting")}
                className="hover:text-white transition"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-xs font-semibold uppercase tracking-widest">
                Compose Sequence
              </span>
            </div>

            {/* Message List */}
            <div className="space-y-3 max-h-60 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-white/20">
              {draftMessages.map((msg, idx) => (
                <div key={idx} className="flex gap-2 items-start group">
                  <div className="pt-3 text-white/50 text-xs font-mono">
                    {idx + 1}
                  </div>
                  <textarea
                    value={msg}
                    onChange={(e) => updateDraftMessage(idx, e.target.value)}
                    className="flex-1 min-h-[3rem] bg-black/20 border border-white/20 rounded-lg p-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-white/30 resize-y text-sm backdrop-blur-sm"
                    placeholder="Type a message..."
                    rows={1}
                  />
                  <button
                    onClick={() => removeMessageBubble(idx)}
                    className="mt-2 text-white/30 hover:text-red-300 transition"
                    title="Remove message"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>

            {/* Footer Actions */}
            <div className="flex justify-between items-center mt-3 pt-3 border-t border-white/10">
              <button
                onClick={addMessageBubble}
                className="flex items-center gap-1.5 text-xs font-medium text-white/70 hover:text-white transition px-2 py-1 rounded hover:bg-white/10"
              >
                <Plus size={14} /> Add Bubble
              </button>

              <button
                onClick={handleSendDraft}
                // Disable if all bubbles are empty
                disabled={draftMessages.every((m) => !m.trim())}
                className="flex items-center gap-2 rounded-xl bg-white/90 px-4 py-2 text-sm font-bold text-blue-900 shadow-lg transition hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send Sequence <Send size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
