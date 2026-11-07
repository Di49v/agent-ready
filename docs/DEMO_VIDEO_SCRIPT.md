# AgentReady Lab — 2:45 Demo Video Script & Storyboard

> **Target Duration:** Exactly 2 minutes and 40 seconds (Hard cap: < 3:00).  
> **Key Takeaway for Judges:** *"PayPal protects the payment. Nobody tests the merchant's side of an agent order. AgentReady Lab does."*

---

## 🎬 Master Timing Breakdown

| Scene | Time Window | Title | Primary Screen Action | Spoken Focus |
|:---:|:---:|---|---|---|
| **Scene 1** | `0:00 – 0:20` | **The Hook & The Story** | Hero banner & problem graphic | Priya's \$160 double charge; agent vs. human checkout failure |
| **Scene 2** | `0:20 – 1:10` | **The Naive Crash Test** | Click **Run Crash Test**; 9 lanes fire | Watch swarm attack; AG Grid turns red (`18/100`); 3 key bugs |
| **Scene 3** | `1:10 – 1:55` | **Dual-Ledger & Diff** | Click double-charge row; open drawer | PayPal Ground Truth vs Store DB; APIMatic 10-line patch |
| **Scene 4** | `1:55 – 2:25` | **Hardened Green Re-Run** | Click **Apply Patch & Re-Run** | Same seed; Guard blocks bugs; score rises to `95/100` (PASS) |
| **Scene 5** | `2:25 – 2:45` | **MCP Ecosystem & Close** | Antigravity IDE MCP call & SVG badge | 5 MCP tools, APIMatic SDK, sponsor roll & final tagline |

---

## 🎙️ Turn-by-Turn Voiceover & Screen Recording Directions

### 📽️ Scene 1: The Hook & The Story (`0:00 – 0:20`)
- **Visual:** Start on the top split-screen hero header of the AgentReady Lab dashboard at `http://localhost:3000`. Show the high-contrast tagline and the 3-card Cart-to-Ledger Mini-Simulator.
- **Voiceover:**
  > *"Priya tells her autonomous AI assistant: 'Buy running shoes, size 8, under \$80.' The assistant pays through PayPal, but the network hiccups before it receives confirmation. The agent automatically retries. The merchant's backend doesn't recognise the idempotency key and creates a second order. PayPal sees two valid authorizations and Priya gets charged \$160 instead of \$80.*  
  > *PayPal did its job. But nobody tests the merchant's side of an agent order. AgentReady Lab does."*

---

### 📽️ Scene 2: The Naive Crash Test (`0:20 – 1:10`)
- **Visual:**
  1. Hover over the **`Target: Naive Shop`** selector.
  2. Click the bright cyan **`Run Crash Test`** button (Seed: `42`).
  3. Watch the 9 horizontal animated persona lanes execute across the 2 waves.
  4. Camera pans down to the AG Grid findings matrix as rows populate with red violation status pills.
  5. The top score ring locks in at **`18 / 100 (FAIL)`**.
- **Voiceover:**
  > *"We built AgentReady Lab as an adversarial crash-testing facility for agentic checkouts. With one click, our swarm engine launches nine specialized buyer test dummies into the store's PayPal Sandbox integration.*  
  > *Notice the 9 lanes: 'The Retrier' drops packets; 'The Tamperer' mutates payload prices; 'The Content Trap' reads prompt-injected product text.*  
  > *In under 15 seconds, the run settles. The store scored an abysmal 18 out of 100. Let's look at the three critical failures: a double charge of \$240 on a \$120 cart, a tampered \$1.50 purchase of \$150 shoes, and an unverified fake webhook that marked an order paid without cryptographic verification."*

---

### 📽️ Scene 3: Dual-Ledger Ground Truth & APIMatic Grounded Patch (`1:10 – 1:55`)
- **Visual:**
  1. In the AG Grid table, click on the top red row: **`Rule 1: Double Capture on Retry Without Idempotency`**.
  2. The **Dual-Ledger Drawer** slides open from the right.
  3. Point the mouse to the split columns:
     - Left column: **PayPal Ground Truth** (`2 captures: 5O190127TN364715T, 7P280238UO475826U`).
     - Right column: **Store Ledger** (`1 internal order recorded`).
  4. Scroll down to show the plain-English explanation referencing the exact PayPal IDs, followed by the **10-line unified Git diff**.
- **Voiceover:**
  > *"When we click the double charge finding, AgentReady Lab doesn't just guess—it performs dual-ledger reconciliation. On the left: PayPal's ground truth proves two independent captures completed for the exact same cart ID. On the right: the merchant's database only knows about one. That is \$120 of unrecorded money.*  
  > *Below, our Fix Engine—grounded directly with the APIMatic Context Plugin for PayPal—explains the root cause and provides the exact 10-line Git patch: persisting the buyer's Idempotency-Key into PayPal-Request-Id."*

---

### 📽️ Scene 4: The Hardened Green Re-Run (`1:55 – 2:25`)
- **Visual:**
  1. Click the green button: **`Apply Patch & Re-Run on Hardened Shop`**.
  2. The swarm re-runs using the exact same random seed (`42`).
  3. The persona lanes animate: this time, `The Retrier` shows `Idempotent-Replayed: true` (green dot). `The Tamperer` shows `409 Price Mismatch` (guarded dot).
  4. The score counter climbs rapidly from `18` to **`95 / 100 (PASS)`**!
  5. Point out the single remaining low-severity finding: *"Honest Black-Box Probe Limitation"*.
- **Voiceover:**
  > *"Now we click 'Apply Patch & Re-Run'. Using the exact same seed, the swarm attacks our Hardened Shop protected by AgentReady Guard middleware.*  
  > *Watch the telemetry: the duplicate retry is recognized and returns the cached payment without double-billing. The tampered price is blocked with an RFC 9457 Problem Details error. The forged webhook is rejected with a 401.*  
  > *Our score climbs from 18 to 95 out of 100. And notice our honest engineering discipline: there is still one residual finding disclosing the boundaries of black-box testing."*

---

### 📽️ Scene 5: MCP Ecosystem, Sponsors & Closing (`2:25 – 2:45`)
- **Visual:**
  1. Cut to **Google Antigravity IDE / VS Code**: show the terminal or chat executing the MCP tool:
     `call tool start_crash_test {"target": "naive-shop", "seed": 42}`.
  2. Cut back to the browser **Deliverables Hub** tab showing the live dynamic SVG badge (`95/100 AGENT-READY`), OpenAPI 3.1 download, and typed `@agent-ready/sdk`.
  3. Close on the sponsor badges: PayPal, APIMatic, AG Grid, Channel3, Render.
- **Voiceover:**
  > *"AgentReady Lab is built API-first. Our stdio MCP server exposes five tools directly to AI coding assistants like Antigravity and Claude Desktop, accompanied by typed SDKs generated via APIMatic.*  
  > *Built with PayPal Sandbox v2, APIMatic, AG Grid Quartz, Channel3, and deployed on Render.*  
  > *PayPal protects the payment. AgentReady Lab protects the merchant. Thank you!"*

---

## 💡 Recording Tips & Checklist

1. **Resolution:** Record at `1920x1080` (1080p, 60fps) in full screen (press `F11` in browser to hide URL bar clutter).
2. **Audio:** Speak clearly with steady pacing; do not rush through the numbers.
3. **Pointers:** Keep cursor movements smooth and purposeful—hover directly over the elements mentioned in the voiceover.
4. **Verification:** Confirm that video duration is between `2:35` and `2:45` before exporting to MP4.

