/**
 * APIMatic-Compatible Typed Client for AgentReady Lab (OpenAPI 3.1).
 * Supports automatic RFC 9457 Problem Details error translation,
 * timeouts, and target store crash testing.
 */
import {
  BenchmarkMatrixResponse,
  FindingDetail,
  LedgerSnapshot,
  PersonaSpec,
  ProblemDetails,
  RerunRequest,
  RunCreateRequest,
  RunReportResponse,
  RunSummary,
  TargetStore,
} from "./models.js";

export interface ClientOptions {
  baseUrl?: string;
  apiKey?: string;
  timeoutMs?: number;
}

export class AgentReadyApiError extends Error {
  public problem: ProblemDetails;
  public status: number;

  constructor(problem: ProblemDetails) {
    super(`[${problem.code}] ${problem.title}: ${problem.detail} (HTTP ${problem.status})`);
    this.name = "AgentReadyApiError";
    this.problem = problem;
    this.status = problem.status;
  }
}

export class AgentReadyClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeoutMs: number;

  constructor(options: ClientOptions = {}) {
    this.baseUrl = (options.baseUrl || "http://localhost:8000").replace(/\/$/, "");
    this.apiKey = options.apiKey;
    this.timeoutMs = options.timeoutMs || 30000;
  }

  private async request<T>(
    path: string,
    method: "GET" | "POST" = "GET",
    body?: any,
    headers: Record<string, string> = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const reqHeaders: Record<string, string> = {
      Accept: "application/json",
      ...headers,
    };

    if (body !== undefined) {
      reqHeaders["Content-Type"] = "application/json";
    }

    if (this.apiKey) {
      reqHeaders["X-Lab-Api-Key"] = this.apiKey;
      reqHeaders["Authorization"] = `Bearer ${this.apiKey}`;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await fetch(url, {
        method,
        headers: reqHeaders,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      if (!response.ok) {
        let problem: ProblemDetails;
        try {
          problem = (await response.json()) as ProblemDetails;
        } catch {
          problem = {
            type: "https://lab.example/errors/unknown",
            title: "HTTP Error",
            status: response.status,
            code: `HTTP_${response.status}`,
            detail: await response.text(),
          };
        }
        throw new AgentReadyApiError(problem);
      }

      const contentType = response.headers.get("content-type") || "";
      if (contentType.includes("application/json")) {
        return (await response.json()) as T;
      }
      return (await response.text()) as unknown as T;
    } finally {
      clearTimeout(timer);
    }
  }

  // ---------------------------------------------------------------------------
  // 1. Health
  // ---------------------------------------------------------------------------
  public async healthCheck(): Promise<{ status: string; version: string; mock_blueprint: boolean }> {
    return this.request("/healthz", "GET");
  }

  // ---------------------------------------------------------------------------
  // 2. Targets
  // ---------------------------------------------------------------------------
  public async listTargets(): Promise<TargetStore[]> {
    return this.request<TargetStore[]>("/v1/targets", "GET");
  }

  public async createTarget(target: TargetStore): Promise<TargetStore> {
    return this.request<TargetStore>("/v1/targets", "POST", target);
  }

  // ---------------------------------------------------------------------------
  // 3. Personas
  // ---------------------------------------------------------------------------
  public async listPersonas(): Promise<PersonaSpec[]> {
    return this.request<PersonaSpec[]>("/v1/personas", "GET");
  }

  // ---------------------------------------------------------------------------
  // 4. Runs & Evaluation
  // ---------------------------------------------------------------------------
  public async createRun(request: RunCreateRequest = {}): Promise<RunSummary> {
    return this.request<RunSummary>("/v1/runs", "POST", request);
  }

  public async getRun(id: string): Promise<RunSummary> {
    return this.request<RunSummary>(`/v1/runs/${id}`, "GET");
  }

  public async getRunFindings(id: string): Promise<FindingDetail[]> {
    return this.request<FindingDetail[]>(`/v1/runs/${id}/findings`, "GET");
  }

  public async getRunLedger(id: string): Promise<LedgerSnapshot> {
    return this.request<LedgerSnapshot>(`/v1/runs/${id}/ledger`, "GET");
  }

  public async getRunReport(id: string): Promise<RunReportResponse> {
    return this.request<RunReportResponse>(`/v1/runs/${id}/report?format=json`, "GET");
  }

  public async getRunReportMarkdown(id: string): Promise<string> {
    return this.request<string>(`/v1/runs/${id}/report?format=markdown`, "GET", undefined, {
      Accept: "text/markdown",
    });
  }

  public async rerunRun(id: string, body?: RerunRequest): Promise<RunSummary> {
    return this.request<RunSummary>(`/v1/runs/${id}/rerun`, "POST", body || {});
  }

  // ---------------------------------------------------------------------------
  // 5. Badges & Benchmark
  // ---------------------------------------------------------------------------
  public async getScoreBadgeSvg(target: string): Promise<string> {
    return this.request<string>(`/v1/badge/${target}.svg`, "GET", undefined, {
      Accept: "image/svg+xml",
    });
  }

  public async getBenchmarkMatrix(): Promise<BenchmarkMatrixResponse> {
    return this.request<BenchmarkMatrixResponse>("/v1/benchmark", "GET");
  }
}

