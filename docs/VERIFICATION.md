# Verification gates and evidence ledger

## Current evidence (2026-11-02)
- Repository existence and initial main README: verified via GitHub.
- GitHub draft PR #1 source foundation: **verified** at commit `2818276deb72b7b0323425da4319df6dc53fc2df`; all 17 changed paths read back from GitHub.
- GitHub Actions `Source structure sanity`: **PASS at the above commit**, run ID `41557541809`. This is only repository structure/manifest checking, **not** Unreal compilation. Subsequent commits require their own status verification.
- Unreal Engine 5.8.4 C++ build: **not run / unverified**.
- Unreal native automation test: **not run / unverified**.
- Editor launch, imports, maps, screenshots, physics and performance: **not run / unverified**.
- Originality/trademark audit: **not cleared**.

## Local static check (can run without Unreal)
```powershell
python tools/check_project_structure.py
```
Passing this checks only repository shape and parseability, not engine compilation.

## Windows Unreal review gate (later, exact path machine-dependent)
1. Open `ArchCityInDarkness.uproject` in installed Unreal Engine 5.8.4.
2. Generate project files if prompted; use matching VS/MSVC build tools.
3. Compile `ArchCityInDarknessEditor` for Win64 Development.
4. Run the Unreal automation test `ArchCityInDarkness.Survival.Hunger.Contract` from the Session Frontend or an explicit unattended Editor command.
5. Record exact engine version, git head SHA, command lines, resulting logs, test counts, and screenshots of the Editor/test status.
6. Document failures on the PR without changing the project's evidence status to PASS.
7. Do not approve assets or claim playability from static checks alone.

## Reversibility
No merge to main until a human review. Prototype artifacts may be reverted without touching unrelated projects. The first milestone carries no irreversible content migration, paid asset dependence, or external service requirement.
