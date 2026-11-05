-- =============================================================================
-- AgentReady Lab — Supabase PostgreSQL Database Schema
-- Run this script in your Supabase SQL Editor to initialize all 10 core tables.
-- =============================================================================

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Targets Table (E-commerce stores registered for auditing)
CREATE TABLE IF NOT EXISTS targets (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    base_url VARCHAR(255) NOT NULL,
    mode VARCHAR(32) DEFAULT 'probe' NOT NULL,
    probe_url VARCHAR(255),
    ledger_secret VARCHAR(128),
    description TEXT,
    is_demo BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 2. Runs Table (Crash-test execution summaries and certifications)
CREATE TABLE IF NOT EXISTS runs (
    run_id VARCHAR(64) PRIMARY KEY,
    target_id VARCHAR(64) REFERENCES targets(id) ON DELETE CASCADE,
    target_name VARCHAR(128) NOT NULL,
    status VARCHAR(32) DEFAULT 'PENDING' NOT NULL,
    score INTEGER,
    passed BOOLEAN DEFAULT FALSE NOT NULL,
    duration_sec FLOAT DEFAULT 0.0 NOT NULL,
    seed INTEGER DEFAULT 42 NOT NULL,
    policy_id VARCHAR(64) DEFAULT 'balanced' NOT NULL,
    total_findings INTEGER DEFAULT 0 NOT NULL,
    critical_count INTEGER DEFAULT 0 NOT NULL,
    high_count INTEGER DEFAULT 0 NOT NULL,
    medium_count INTEGER DEFAULT 0 NOT NULL,
    low_count INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_runs_target_id ON runs(target_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);

-- 3. Attempts Table (Individual persona lane executions)
CREATE TABLE IF NOT EXISTS attempts (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) REFERENCES runs(run_id) ON DELETE CASCADE,
    persona_id VARCHAR(64) NOT NULL,
    lane_number INTEGER NOT NULL,
    cart_id VARCHAR(64) NOT NULL,
    status VARCHAR(32) DEFAULT 'PENDING' NOT NULL,
    last_action VARCHAR(128),
    amount VARCHAR(32),
    paypal_order_id VARCHAR(64),
    paypal_capture_id VARCHAR(64),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_attempts_run_id ON attempts(run_id);
CREATE INDEX IF NOT EXISTS idx_attempts_cart_id ON attempts(cart_id);
CREATE INDEX IF NOT EXISTS idx_attempts_persona_id ON attempts(persona_id);

-- 4. PayPal Records Table (Ground truth snapshot from PayPal Sandbox)
CREATE TABLE IF NOT EXISTS paypal_records (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) REFERENCES runs(run_id) ON DELETE CASCADE,
    cart_id VARCHAR(64) NOT NULL,
    order_id VARCHAR(64),
    capture_id VARCHAR(64),
    status VARCHAR(32) NOT NULL,
    amount VARCHAR(32) NOT NULL,
    currency VARCHAR(16) DEFAULT 'USD' NOT NULL,
    raw_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_paypal_records_run_id ON paypal_records(run_id);
CREATE INDEX IF NOT EXISTS idx_paypal_records_cart_id ON paypal_records(cart_id);

-- 5. Store Records Table (Store ledger state retrieved via /_lab/ledger Probe or Observer)
CREATE TABLE IF NOT EXISTS store_records (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) REFERENCES runs(run_id) ON DELETE CASCADE,
    cart_id VARCHAR(64) NOT NULL,
    order_id VARCHAR(64),
    status VARCHAR(32) NOT NULL,
    amount VARCHAR(32) NOT NULL,
    probe_accessible BOOLEAN DEFAULT TRUE NOT NULL,
    raw_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_store_records_run_id ON store_records(run_id);
CREATE INDEX IF NOT EXISTS idx_store_records_cart_id ON store_records(cart_id);

-- 6. Findings Table (Identified commerce invariant violations)
CREATE TABLE IF NOT EXISTS findings (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) REFERENCES runs(run_id) ON DELETE CASCADE,
    rule_number INTEGER NOT NULL,
    rule_name VARCHAR(128) NOT NULL,
    severity VARCHAR(32) NOT NULL,
    category VARCHAR(64) NOT NULL,
    persona_id VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    evidence_ids JSONB DEFAULT '[]'::jsonb NOT NULL,
    paypal_record JSONB,
    store_record JSONB,
    explanation TEXT NOT NULL,
    patch_diff TEXT,
    fixed BOOLEAN DEFAULT FALSE NOT NULL,
    remediation_action VARCHAR(128),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_findings_run_id ON findings(run_id);

-- 7. Patches Table (Autonomous git diff remediations)
CREATE TABLE IF NOT EXISTS patches (
    id VARCHAR(64) PRIMARY KEY,
    finding_id VARCHAR(64),
    target_id VARCHAR(64) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    diff_content TEXT NOT NULL,
    applied BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_patches_target_id ON patches(target_id);

-- 8. Run Event Logs Table (Sequential telemetry event log for SSE streaming & replay)
CREATE TABLE IF NOT EXISTS run_event_logs (
    id BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(64) REFERENCES runs(run_id) ON DELETE CASCADE,
    event_id VARCHAR(64) NOT NULL,
    seq INTEGER NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    lane INTEGER,
    timestamp VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_run_events_run_id_seq ON run_event_logs(run_id, seq);

-- 9. Store Orders Table (Internal store database for demo shops)
CREATE TABLE IF NOT EXISTS store_orders (
    order_id VARCHAR(64) PRIMARY KEY,
    cart_id VARCHAR(64) UNIQUE NOT NULL,
    status VARCHAR(32) DEFAULT 'CREATED' NOT NULL,
    amount VARCHAR(32) NOT NULL,
    currency VARCHAR(16) DEFAULT 'USD' NOT NULL,
    customer_email VARCHAR(128),
    paypal_order_id VARCHAR(64),
    paypal_capture_id VARCHAR(64),
    tracking_number VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_store_orders_cart_id ON store_orders(cart_id);

-- 10. Idempotency Records Table (Idempotency key locks and cached responses for Guard middleware)
CREATE TABLE IF NOT EXISTS idempotency_records (
    idempotency_key VARCHAR(128) PRIMARY KEY,
    target_id VARCHAR(64) NOT NULL,
    request_hash VARCHAR(64) NOT NULL,
    status_code INTEGER NOT NULL,
    response_headers JSONB DEFAULT '{}'::jsonb NOT NULL,
    response_body JSONB DEFAULT '{}'::jsonb NOT NULL,
    locked BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_idempotency_records_target_id ON idempotency_records(target_id);

-- Seed Initial Demo Targets
INSERT INTO targets (id, name, base_url, mode, probe_url, ledger_secret, description, is_demo)
VALUES 
    (
        'naive-shop',
        'Naive Shop (Vulnerable Baseline)',
        'http://localhost:8000/demo/naive',
        'probe',
        'http://localhost:8000/demo/naive/_lab/ledger',
        'mock_naive_probe_secret_32bytes_hex',
        'Reference e-commerce store with common AI commerce flaws: missing idempotency, unverified webhooks, client price trust.',
        TRUE
    ),
    (
        'hardened-shop',
        'Hardened Shop (Guard Protected)',
        'http://localhost:8000/demo/hardened',
        'probe',
        'http://localhost:8000/demo/hardened/_lab/ledger',
        'mock_hardened_probe_secret_32bytes_hex',
        'Hardened store protected by AgentReady Guard middleware: idempotency cache, server price recomputation, RFC 9457 structured errors.',
        TRUE
    )
ON CONFLICT (id) DO NOTHING;

