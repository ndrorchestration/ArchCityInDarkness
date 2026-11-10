# ACID-HIP v0.1 — supervised pilot instructions

**Namespace:** ACID-HIP = Arch City in Darkness Handoff Interoperability Pilot. ACP is reserved exclusively for the separate Agent Control Plane architecture. Historical mentions of ACP-PILOT-001 in old notes and PR links refer to ACID-HIP-001; do not interpret them as ACP work.\n\nStatus: DRAFT / NON-OPERATIONAL. This file describes a proposed interoperability pilot; it does not grant any tool permission, initiate agents, or imply an approved game feature.

## Mission
Test evidence-based coordination among ChatGPT (scope and adjudication), Hermes (bounded implementation candidate), and Herald / Meta Muse Code (independent review), using GitHub as the durable task and evidence record and RDC/Neontic solely for authorized local execution.

## Non-negotiable boundaries
- Never work on `main` or merge without explicit human approval; use a distinct branch/worktree per writer.
- Never run an agent with `--yolo` or equivalent blanket approval in this pilot.
- Reviewers must not modify the implementer's branch or share its worktree.
- No unattended destructive shell commands, credential disclosure, production deployment, paid API invocation without budget, or automatic game-canon changes.
- Use minimal repo scopes; do not read/write unrelated repositories.
- An AI summary or successful CLI exit is not evidence of passing tests. Record exact commit, commands, exit codes, outputs, and unresolved failures.
- Source checks are not native Unreal Editor/PIE/runtime or visual verification.
- If agent identity, auth, workspace trust, costs, or scope is unclear: fail closed and surface blocker.
- Do not change any DGAF scientific or governance state. This pilot is confined to ArchCityInDarkness.

## Roles
1. ChatGPT: scope task and acceptance criteria; reconcile evidence; recommend disposition. Cannot represent an unattended active orchestrator.
2. Hermes: bounded task implementation in its own worktree; generate explicit evidence and draft PR; no merge.
3. Herald (Muse Code): independent, preferably read-only, review of a pinned commit and explicit requirements; separate workspace; review report only.
4. GitHub CI: objective checks; independent of the agents' claims.
5. Human: approves merges, canon, expansion of permissions and high-impact operations.

## Handoff contract
A task contains: ID, objective, owner, pinned base SHA, allowed paths, forbidden actions, acceptance checks, dependency list, budget caps and a reviewer.
Implementation output: branch, head SHA, diff summary, test commands + exit codes, artifacts, outstanding risks, draft PR.
Review output: reviewed head SHA, explicit requirements coverage, defects with file references, unverified claims, disposition (PASS / FAIL / BLOCKED).
Reconciliation: do not promote status if the review references a stale SHA or required evidence is missing.

## Initial pilot
The first proposed task is documentation/schema validation only; no gameplay change, native Unreal build, autonomous scheduled run or merge until the two agent runtimes are verified.
