export type InputType = "text" | "image" | "audio" | "file";

export interface PromptConfig {
  id: string;
  title: string;
  summary: string;
  systemPrompt: string;
  addSysPrompt: string[];
  model: string;
  inputs: InputType[];
  persistInputs: ("text" | "file")[];
}
