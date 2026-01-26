export interface ReplyOption {
  label: string;
  text: string[];
  sentiment: "positive" | "negative" | "neutral";
}

export interface DashboardCard {
  id: string; // Don't forget the ID used for deletion
  chat_id: number;
  sender: string;
  summary: string;
  urgency: "low" | "medium" | "high";
  suggested_action: "ignore" | "reply" | "calendar_event";
  reply_options: ReplyOption[]; // Array of options
  calendar_details?: {
    title: string;
    date: string;
    time?: string;
  };
}
