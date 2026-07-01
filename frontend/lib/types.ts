export interface RetrievedDoc {
  doc_id: string;
  title: string;
  doc_type: string;
  year: number;
  date: string;
  author: string;
  content: string;
  fused_score: number;
  fused_rank: number;
  rerank_score: number | null;
  final_rank: number;
  rank_delta: number;
}

export interface TraceEvent {
  tool: string;
  args: Record<string, unknown>;
  results: RetrievedDoc[];
  trace: {
    query: string;
    mode: string;
    candidates_considered: number;
  };
}

export interface MemoryHit {
  score: number;
  question: string;
  summary: string;
}

export interface ChatResponse {
  answer: string;
  mode: string;
  tool_calls: string[];
  retrieval_trace: TraceEvent[];
  memory_hits: MemoryHit[];
  latency_ms: number;
}

export interface ChatMessage {
  role: "user" | "agent";
  text: string;
  mode?: string;
  latency_ms?: number;
}
