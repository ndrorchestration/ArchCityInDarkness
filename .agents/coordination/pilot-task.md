# ACID-HIP-001 — Interoperability handshake

**Identity:** ACID-HIP-001 (formerly labeled ACP-PILOT-001 in historical handoffs). Not part of the Agent Control Plane (ACP).\n\nStatus: BLOCKED pending Herald runtime discovery and both agents' explicit controlled test authorization.
This is a planning artifact only, not an instruction to execute automatically.

## Objective
Demonstrate that Hermes can prepare one safe, reviewable documentation/schema patch and Herald can independently review that exact commit without writing to the implementer's branch.

## Allowed surface
Only `.agents/coordination/` files on an additional isolated pilot branch/worktree. No gameplay source, GitHub settings, secrets, workflows, or third-party assets.

## Sequence
1. Capture tool versions, auth readiness *without secrets*, repo base SHA and disk/memory headroom.
2. Scope a tiny task: amend the proposed handoff schema, add example valid/invalid payloads, and use offline validation (no package installation).
3. Hermes implements on its own worktree/branch, records head SHA, test command and exit status, and opens draft PR.
4. Herald examines pinned SHA in separate read-only workspace and delivers independent PASS/FAIL/BLOCKED report with specific defects.
5. CI or operator independently validates schema. ChatGPT reconciles exact-head reports and recommends accept/rework; user authorizes merge.

## Acceptance criteria
- Distinct implementation and review workspaces.
- An evidence manifest contains task ID, base/head SHA, allowed paths, commands, exit codes and outputs.
- Negative example fails and positive example passes offline validation.
- Herald report cites the same reviewed SHA as the submitted candidate.
- No autonomous merges, external charges, destructive commands, or canon changes.
- Missing runtime/auth/test evidence leaves pilot BLOCKED rather than passed.

## Current observed blockers (2026-11-10)
- Hermes Agent v0.22.5 detected on Neontic; gateway reports running, but no authenticated controlled task was executed for this pilot.
- Meta Muse Code `muse` was not found on PATH or several common install locations; could be elsewhere, but headless readiness is unverified.
- No interoperability handshake has been executed.
