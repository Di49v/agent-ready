/**
 * APIMatic-Compatible Data Models for AgentReady Lab (OpenAPI 3.1).
 * Strictly mirrors backend contracts and RFC 9457 Problem Details schemas.
 */

export type RunStatus = "queued" | "running" | "grading" | "complete" | "failed";
export type AutoReversalPolicy = "observe" | "assist" | "auto";
export type FindingSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export interface TargetStore {
  id: string;
  name: string;
  base_url: string;
  mode?: "probe" | "black_box";
  probe_url?: string;
  ledger_secret?: string;
  description?: string;
  is_demo?: boolean;
  created_at?: string;
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
  wave?: number;
}

export interface RunCreateRequest {
  target?: string;
  pack?: string;
  seed?: number;
  policy?: AutoReversalPolicy;
  replay?: boolean;
  callback_url?: string;
}

export interface RerunRequest {
  target_override?: string;
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
  rule_number: number;
  rule_name: string;
  severity: FindingSeverity;
  persona_id: string;
  title: string;
  explanation: string;
  evidence_ids: string[];
  patch_diff?: string;
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
  timestamp: string;
  total_rows: number;
  discrepancy_count: number;
  dual_rows: DualLedgerRow[];
  is_black_box?: boolean;
}

export interface RunSummary {
  id: string;
  target: string;
  target_name: string;
  status: RunStatus;
  score?: number;
  seed: number;
  policy: AutoReversalPolicy;
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

export interface RunReportResponse {
  run_id: string;
  summary: RunSummary;
  markdown: string;
  generated_at: string;
}

export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  code: string;
  detail: string;
  instance?: string;
  retryable?: boolean;
  next_action?: string;
  details?: Record<string, any>;
}

export interface BenchmarkMatrixItem {
  bug_flag: string;
  rule_number: number;
  rule_name: string;
  title: string;
  severity: string;
  template_explanation: string;
  grounded_api_note: string;
  patch_diff: string;
  remediation_action: string;
}

export interface BenchmarkMatrixResponse {
  bugs: BenchmarkMatrixItem[];
  total: number;
}

