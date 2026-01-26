export type InputType = "text" | "image" | "audio" | "file";

export interface PromptConfig {
  title: string;
  summary: string;
  systemPrompt: string;
  model: string;
  inputs: InputType[];
}

export interface PromptTemplate {
  id: string;
  title: string;
  summary: string;
  inputs: InputType[];
  defaultSystemPrompt: string;
  defaultModel: string;
}
