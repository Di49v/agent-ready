/**
 * AgentReady Lab — Frontend API Client & Contracts
 * Communicates with FastAPI backend on http://localhost:8000
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// -----------------------------------------------------------------------------
// Data Contracts (Matching Backend Pydantic v2 Models)
// -----------------------------------------------------------------------------

export interface TargetStore {
  id: string;
  name: string;
  base_url: string;
  mode: "probe" | "black_box";
  probe_url?: string;
  ledger_secret?: string;
  description?: string;
  is_demo?: boolean;
}

export interface PersonaSpec {
  id: string;
  name: string;
  plain_words: string;
  rule_number: number;
  rule_name: string;
  driven_by: "fixed_script" | "live_llm";
  fault_description: string;
  expected_behavior: string;
  wave: number;
}

export interface RuleScore {
  rule_number: number;
  rule_name: string;
  weight: number;
  failed_carts: number;
  total_evaluated_carts: number;
  failure_share: number;
  rule_score: number;
  status: "PASS" | "FAIL";
}

export interface FindingDetail {
  id: string;
  run_id?: string;
  rule_number: number;
  rule_name: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  persona_id?: string;
  title: string;
  evidence_ids: string[];
  paypal_record?: Record<string, any>;
  store_record?: Record<string, any>;
  explanation: string;
  patch_diff?: string;
  fixed?: boolean;
  remediation_action?: string;
}

export interface DualLedgerRow {
  cart_id: string;
  persona_id: string;
  timestamp: string;
  paypal_order_id?: string;
  paypal_capture_id?: string;
  paypal_status?: string;
  paypal_amount?: string;
  store_order_id?: string;
  store_status?: string;
  store_amount?: string;
  tracking_number?: string;
  has_dispute?: boolean;
  dispute_id?: string;
  disagreements: string[];
}

export interface LedgerSnapshot {
  run_id: string;
  target_id: string;
  snapshot_time: string;
  settle_window_sec: number;
  probe_verified: boolean;
  paypal_records: Record<string, any>[];
  store_records: Record<string, any>[];
  dual_rows: DualLedgerRow[];
}

export interface RunSummary {
  id: string;
  target: string;
  target_name: string;
  status: "queued" | "running" | "grading" | "complete" | "failed";
  score?: number;
  seed: number;
  policy: "observe" | "assist" | "auto";
  pack: string;
  created_at: string;
  completed_at?: string;
  settle_window_sec: number;
  total_findings: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  findings: FindingDetail[];
  rule_scores: RuleScore[];
  badge_url?: string;
  disclaimer: string;
}

export interface RunCreateRequest {
  target: string;
  pack?: string;
  seed?: number;
  policy?: "observe" | "assist" | "auto";
  replay?: boolean;
}

export interface RunEvent {
  event: "agent_step" | "paypal_event" | "store_ledger_row" | "finding" | "run_completed";
  run_id: string;
  timestamp: string;
  lane?: number;
  persona_id?: string;
  actor?: string;
  action?: string;
  paypal_id?: string;
  amount?: string;
  status?: string;
  rule_hit?: number;
  data?: Record<string, any>;
}

export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  code: string;
  detail?: string;
  retryable?: boolean;
  next_action?: string;
  details?: Record<string, any>;
}

// -----------------------------------------------------------------------------
// API Client Functions
// -----------------------------------------------------------------------------

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetails: ProblemDetails | null = null;
    try {
      errorDetails = await res.json();
    } catch {
      // not JSON
    }
    const message =
      errorDetails?.title || errorDetails?.detail || `HTTP ${res.status}: ${res.statusText}`;
    const err = new Error(message) as Error & { problem?: ProblemDetails; status: number };
    err.problem = errorDetails || undefined;
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export async function fetchTargets(): Promise<TargetStore[]> {
  const res = await fetch(`${API_BASE_URL}/v1/targets`);
  return handleResponse<TargetStore[]>(res);
}

export async function fetchPersonas(): Promise<PersonaSpec[]> {
  const res = await fetch(`${API_BASE_URL}/v1/personas`);
  return handleResponse<PersonaSpec[]>(res);
}

export async function createRun(req: RunCreateRequest): Promise<RunSummary> {
  const res = await fetch(`${API_BASE_URL}/v1/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return handleResponse<RunSummary>(res);
}

export async function getRun(runId: string): Promise<RunSummary> {
  const res = await fetch(`${API_BASE_URL}/v1/runs/${runId}`);
  return handleResponse<RunSummary>(res);
}

export async function getRunFindings(runId: string): Promise<FindingDetail[]> {
  const res = await fetch(`${API_BASE_URL}/v1/runs/${runId}/findings`);
  return handleResponse<FindingDetail[]>(res);
}

export async function getRunLedger(runId: string): Promise<LedgerSnapshot> {
  const res = await fetch(`${API_BASE_URL}/v1/runs/${runId}/ledger`);
  return handleResponse<LedgerSnapshot>(res);
}

export async function rerunRun(
  baseRunId: string,
  targetOverride?: string
): Promise<RunSummary> {
  const res = await fetch(`${API_BASE_URL}/v1/runs/${baseRunId}/rerun`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_override: targetOverride }),
  });
  return handleResponse<RunSummary>(res);
}

/**
 * Connects to the SSE telemetry stream for live swarm lanes.
 * Returns a teardown function to safely close the EventSource.
 */
export function subscribeRunEvents(
  runId: string,
  onEvent: (event: RunEvent) => void,
  onComplete: () => void,
  onError: (err: any) => void
): () => void {
  const url = `${API_BASE_URL}/v1/runs/${encodeURIComponent(runId)}/events`;
  const eventSource = new EventSource(url);

  const eventTypes: Array<RunEvent["event"]> = [
    "agent_step",
    "paypal_event",
    "store_ledger_row",
    "finding",
    "run_completed",
  ];

  eventTypes.forEach((type) => {
    eventSource.addEventListener(type, (e: MessageEvent) => {
      try {
        const parsed: RunEvent = JSON.parse(e.data);
        onEvent(parsed);
        if (type === "run_completed") {
          eventSource.close();
          onComplete();
        }
      } catch (err) {
        console.error("Failed to parse SSE event payload:", err);
      }
    });
  });

  eventSource.onerror = (err) => {
    console.warn("SSE connection encountered error or closed:", err);
    eventSource.close();
    onError(err);
  };

  return () => {
    eventSource.close();
  };
}

