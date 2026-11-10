# Daily development log — review-only implementation

For Arch City in Darkness, the proposed workflow is not active until reviewed and merged to the repository default branch. It does not authorize a merge, release, original canon change, third-party IP promotion, or bypass of an existing gate.

## How it works

At 11:00 UTC, safely after New York midnight year-round, GitHub Actions builds an evidence-index report for the previous full America/New_York calendar day. It records default-branch commits, recently updated PRs and issues, fix-labeled changes, experiments identified by titles, and GitHub Actions results. The record is stored at docs/devlog/YYYY-MM-DD.md on branch automation/daily-devlog, **never on protected main**. Re-running an unchanged report is a no-op.

Inspect generated records using the branch selector in GitHub (automation/daily-devlog). The source workflow is .github/workflows/daily-devlog.yml; pure JavaScript logic and tests live in tools/devlog. Only standard Node and GitHub Actions permissions are required.

Limitations: first 100 records per API category; this repository only; default-branch commits only; updated PRs are not necessarily completed work; CI is not Unreal native build, PIE, GPU, creator approval, or playable-slice evidence. GitHub-only logs cannot capture unpushed workstation activity or Notion-only work. No private sources should be published here.

The dedicated Notion [Arch City in Darkness — Game Development Log](https://app.notion.com/p/15d6d984aad8453a846d29bc6bc736f7) records local work, native verification and game production stages separately. The [ecosystem overview](https://app.notion.com/p/b43e97712d2642c988704fdcf113a45f) only links or summarizes game records, not a second authoritative history. The Notion log is not automatically populated by this repository-local workflow. Do not place private design notes or licensed assets into this public repository.

## Verification and activation

1. Run the unit tests in the draft PR and inspect the exact-head CI result.
2. Review the workflow and authorize a merge through existing repository protections.
3. After merge, inspect the first scheduled or manual workflow run, then its output branch and date-stamped record.
4. If the GitHub token lacks branch-creation permission or CI fails, retain the failure and repair on a review branch. Never bypass protected main or claim automation is operating before an actual hosted run.
