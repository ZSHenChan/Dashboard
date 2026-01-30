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
  Clock,
  History,
} from "lucide-react";
import { DashboardCard, ReplyOption, ReplyMetadata } from "./reply-types";
import { getUrgencyColor, getButtonColor } from "../utils";

type EventCardProps = {
  card: DashboardCard;
  onAction: (
    card: DashboardCard,
    action: "ignore" | "reply",
    payload?: {
      messages: string[];
      meta: ReplyMetadata;
    },
  ) => void;
};

// --- CUSTOM HOOK: Handles the draft logic ---
function useDraftSequence(initialMessages: string[] = [""]) {
  const [draftMessages, setDraftMessages] = useState<string[]>(initialMessages);

  const updateMessage = (index: number, val: string) => {
    const newMsgs = [...draftMessages];
    newMsgs[index] = val;
    setDraftMessages(newMsgs);
  };

  const addBubble = () => setDraftMessages((prev) => [...prev, ""]);

  const removeBubble = (index: number) => {
    if (draftMessages.length === 1) {
      updateMessage(0, "");
      return;
    }
    setDraftMessages((prev) => prev.filter((_, i) => i !== index));
  };

  const setSequence = (msgs: string[]) => setDraftMessages([...msgs]);

  const isValid = draftMessages.some((m) => m.trim() !== "");

  return {
    draftMessages,
    updateMessage,
    addBubble,
    removeBubble,
    setSequence,
    isValid,
  };
}

// --- SUB-COMPONENT: View 1 (Initial) ---
const InitialView = ({
  onReply,
  onIgnore,
}: {
  onReply: () => void;
  onIgnore: () => void;
}) => (
  <div className="mt-4 flex gap-3 animate-in fade-in slide-in-from-top-2 duration-300">
    <button
      onClick={onReply}
      className="flex items-center gap-2 rounded-xl bg-white/80 px-4 py-2 text-sm font-semibold text-blue-900 shadow-sm transition hover:bg-white"
    >
      <MessageSquare size={16} /> Reply
    </button>
    <button
      onClick={onIgnore}
      className="rounded-xl border border-white/30 bg-black/20 px-4 py-2 text-sm font-medium text-white transition hover:bg-black/30"
    >
      Ignore
    </button>
  </div>
);

// --- SUB-COMPONENT: View 2 (Selection Grid) ---
const SelectionView = ({
  options,
  onSelect,
  onEdit,
  onCustom,
}: {
  options: ReplyOption[];
  onSelect: (opt: ReplyOption) => void;
  onEdit: (opt: ReplyOption) => void;
  onCustom: () => void;
}) => (
  <div className="mt-6 animate-in fade-in zoom-in-95 duration-300">
    <span className="text-xs font-semibold uppercase tracking-widest text-white/60 mb-3 block">
      Select or Edit Response
    </span>
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {options.map((option, idx) => (
        <div
          key={idx}
          className={`group relative flex flex-col items-start p-3 rounded-lg border transition-all ${getButtonColor(
            option.sentiment,
          )}`}
        >
          <button
            className="w-full text-left h-full"
            onClick={() => onSelect(option)}
          >
            <div className="flex justify-between w-full">
              <span className="font-bold text-sm uppercase tracking-wider opacity-90">
                {option.label}
              </span>
              {option.text.length > 1 && (
                <span className="flex items-center gap-1 text-[10px] bg-white/20 px-1.5 rounded-md">
                  <Layers size={10} /> +{option.text.length - 1}
                </span>
              )}
            </div>
            <span className="block text-xs opacity-80 mt-1 line-clamp-2 pr-6">
              &quot;{option.text[0]}&quot;
            </span>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit(option);
            }}
            className="absolute top-2 right-2 p-1.5 rounded-full bg-white/10 hover:bg-white/30 text-white opacity-0 group-hover:opacity-100 transition-opacity"
            title="Edit sequence"
          >
            <Pencil size={12} />
          </button>
        </div>
      ))}
      <button
        onClick={onCustom}
        className="flex flex-col items-center justify-center p-3 rounded-lg border border-dashed border-white/40 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition-all min-h-[80px]"
      >
        <Plus size={24} className="mb-1 opacity-70" />
        <span className="text-xs font-medium uppercase tracking-wider">
          Custom
        </span>
      </button>
    </div>
  </div>
);

// --- SUB-COMPONENT: View 3 (Composer) ---
const ComposerView = ({
  draftMessages,
  onUpdate,
  onRemove,
  onAdd,
  onSend,
  onBack,
  isValid,
}: {
  draftMessages: string[];
  onUpdate: (idx: number, val: string) => void;
  onRemove: (idx: number) => void;
  onAdd: () => void;
  onSend: () => void;
  onBack: () => void;
  isValid: boolean;
}) => (
  <div className="mt-6 animate-in fade-in slide-in-from-right-4 duration-300">
    <div className="flex items-center gap-2 mb-3 text-white/70">
      <button onClick={onBack} className="hover:text-white transition">
        <ChevronLeft size={16} />
      </button>
      <span className="text-xs font-semibold uppercase tracking-widest">
        Compose Sequence
      </span>
    </div>

    <div className="space-y-3 max-h-60 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-white/20">
      {draftMessages.map((msg, idx) => (
        <div key={idx} className="flex gap-2 items-start group">
          <div className="pt-3 text-white/50 text-xs font-mono">{idx + 1}</div>
          <textarea
            value={msg}
            onChange={(e) => onUpdate(idx, e.target.value)}
            className="flex-1 min-h-[3rem] bg-black/20 border border-white/20 rounded-lg p-2 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-white/30 resize-y text-sm backdrop-blur-sm"
            placeholder="Type a message..."
            rows={1}
          />
          <button
            onClick={() => onRemove(idx)}
            className="mt-2 text-white/30 hover:text-red-300 transition"
          >
            <Trash2 size={14} />
          </button>
        </div>
      ))}
    </div>

    <div className="flex justify-between items-center mt-3 pt-3 border-t border-white/10">
      <button
        onClick={onAdd}
        className="flex items-center gap-1.5 text-xs font-medium text-white/70 hover:text-white transition px-2 py-1 rounded hover:bg-white/10"
      >
        <Plus size={14} /> Add Bubble
      </button>
      <button
        onClick={onSend}
        disabled={!isValid}
        className="flex items-center gap-2 rounded-xl bg-white/90 px-4 py-2 text-sm font-bold text-blue-900 shadow-lg transition hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Send Sequence <Send size={14} />
      </button>
    </div>
  </div>
);

const ContextView = ({ history }: { history: string[] }) => (
  <div className="mb-4 overflow-hidden rounded-xl border border-white/10 bg-black/20 p-3 animate-in fade-in slide-in-from-top-1">
    <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-white/40">
      <Clock size={10} /> Previous Context
    </div>

    <div className="flex flex-col gap-2 max-h-48 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
      {history.length === 0 ? (
        <span className="text-xs text-white/30 italic">
          No history available
        </span>
      ) : (
        history.map((msg, idx) => (
          <div key={idx} className="flex gap-2">
            {/* Simple visual indicator for the thread line */}
            <div className="flex flex-col items-center">
              <div className="h-full w-px bg-white/10"></div>
            </div>

            <div className="rounded-lg bg-white/5 p-2 text-xs text-white/80 backdrop-blur-sm w-full">
              {msg}
            </div>
          </div>
        ))
      )}
    </div>
  </div>
);

// --- MAIN COMPONENT ---
export function EventCard({ card, onAction }: EventCardProps) {
  const [mode, setMode] = useState<"initial" | "selecting" | "composing">(
    "initial",
  );
  const [currentMeta, setCurrentMeta] = useState<ReplyMetadata>({
    label: "Custom",
    sentiment: "neutral",
    is_custom: true,
  });
  const [showContext, setShowContext] = useState(false);

  // Use our custom hook to separate state logic from UI
  const draft = useDraftSequence();

  const handleQuickReply = (option: ReplyOption) => {
    onAction(card, "reply", {
      messages: option.text,
      meta: {
        label: option.label,
        sentiment: option.sentiment,
        is_custom: false,
      },
    });
  };

  const handleEditOption = (option: ReplyOption) => {
    draft.setSequence(option.text);
    setCurrentMeta({
      label: option.label,
      sentiment: option.sentiment,
      is_custom: false,
    });
    setMode("composing");
  };

  const handleCustomReply = () => {
    draft.setSequence([""]);
    setCurrentMeta({
      label: "Custom Reply",
      sentiment: "neutral",
      is_custom: true,
    });
    setMode("composing");
  };

  const handleSendDraft = () => {
    const cleanMessages = draft.draftMessages.filter((m) => m.trim() !== "");
    if (cleanMessages.length === 0) return;

    onAction(card, "reply", {
      messages: cleanMessages,
      meta: currentMeta, // Pass the stored metadata
    });
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
        {/* Header Section */}
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <div className="flex items-center gap-2.5 mb-2">
              <span
                className={`h-2.5 w-2.5 rounded-full shadow-[0_0_10px] ${getUrgencyColor(
                  card.urgency,
                )}`}
              />
              <h3 className="text-lg font-bold text-white drop-shadow-sm leading-none">
                {card.sender}
              </h3>
            </div>
            <p
              className={`text-white/70 font-medium transition-opacity ${showContext ? "opacity-50 mb-4" : "mb-0"}`}
            >
              {card.summary}
            </p>
            {showContext && <ContextView history={card.conversation_history} />}
          </div>

          <button
            onClick={() => setShowContext(!showContext)}
            className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium transition-all ${
              showContext
                ? "bg-white text-blue-900 shadow-md"
                : "bg-white/10 text-white hover:bg-white/20"
            }`}
          >
            <History size={12} />
            {showContext ? "Hide Context" : "Context"}
          </button>

          {mode !== "initial" && (
            <button
              onClick={() => setMode("initial")}
              className="text-white/50 hover:text-white transition p-1 -mt-1 -mr-1"
            >
              <X size={20} />
            </button>
          )}
        </div>

        {/* Dynamic Body Content */}
        <div className="relative">
          {mode === "initial" && (
            <InitialView
              onReply={() => setMode("selecting")}
              onIgnore={() => onAction(card, "ignore")}
            />
          )}

          {mode === "selecting" && (
            <SelectionView
              options={card.reply_options}
              onSelect={(option) => handleQuickReply(option)}
              onEdit={handleEditOption}
              onCustom={handleCustomReply}
            />
          )}

          {mode === "composing" && (
            <ComposerView
              draftMessages={draft.draftMessages}
              onUpdate={draft.updateMessage}
              onRemove={draft.removeBubble}
              onAdd={draft.addBubble}
              onSend={handleSendDraft}
              onBack={() => setMode("selecting")}
              isValid={draft.isValid}
            />
          )}
        </div>
      </div>
    </div>
  );
}
