export interface ReplyOption {
  label: string;
  text: string[];
  sentiment: "positive" | "negative" | "neutral";
}

export interface DashboardCard {
  id: string;
  chat_id: number;
  title: string;
  summary: string;
  urgency: "low" | "medium" | "high";
  suggested_action: "ignore" | "reply" | "calendar_event";
  reply_options: ReplyOption[];
  conversation_history: string[];
  calendar_details?: {
    title: string;
    date: string;
    time?: string;
  };
}

export interface ReplyMetadata {
  label: string;
  sentiment: "positive" | "negative" | "neutral";
  is_custom: boolean;
}
