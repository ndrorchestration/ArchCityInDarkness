# ART-PILOT-001 — Mara Vale Daz Studio 6 / MetaHuman comparison

**Review-only. Original fictional character. Not canon. Not an asset import.**

This pilot is **independent from the M001–M007 gameplay PR chain**. It prepares a reversible, low-cost side-by-side cinematic character evaluation for *Arch City in Darkness*. The Daz Install Manager is running on the workstation at the last verified check; it must **not** be stopped, restarted, bypassed or modified by an agent.

## Evidence snapshot — Nov 3, 2026 ET

A read-only Windows inspection of connected workstation `neontic` showed:

- `C:\Program Files\DAZ 3D\DAZStudio6\DAZStudio.exe`: **present**, version metadata empty; **not launched or runtime verified**.
- `C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe`: **present**; file metadata reports `++UE5+Release-5.8-CL-58902052`. No native game build/test proof.
- Install Manager processes `DAZ3DIM` and `DAZ3DIMHelper`: **running**. Download completion was not proven.
- Conventional Daz Studio 6/4 `dzunrealbridge.dll` and UE engine-level `DazToUnreal` plug-in paths: **not found** in the explicit locations inspected, not an exhaustive search. Bridge compatibility is not proven.
- System drive C: only **3.17 GiB free**. This does not offer safe headroom for experimental engine builds, new downloaded assets, or shader/DerivedDataCache expansion. Pilot environment probe uses a **conservative 15 GiB minimum** policy for an initial test; this is an operational threshold, not an official Daz/Unreal requirement.
- No UE Editor/Live Coding process observed at that inspection. Do not assume subsequent process state is unchanged.

These are timestamps, not evergreen machine facts. Recheck before a native test.

## Source-only readiness check

On Windows, in an **isolated checkout of this art-pilot branch**, run:

```powershell
.\tools\Get-ArtPilotReadiness.ps1
```

This read-only PowerShell probe emits JSON summarizing **known standard paths**, system-drive space, observed process names and explicit blockers. It starts or stops no apps, writes no files, installs nothing, and **always keeps production import unauthorized** until separate approval. A successful probe exit only means that the probe ran; it is **not a green light to import**.

Run portable manifest checks without Unreal:

```powershell
python tools/validate_art_pilot.py
python -m unittest discover -s tools/tests -p "test_*.py" -v
```

The [original comparison manifest](../ArtPipeline/MaraVale/art_pilot_v1.json) identifies two candidate slots, five matched camera compositions, and required review criteria. It contains **no Daz models, textures, likenesses or other licensed files**. Evidence and licensing must be reviewed per asset **outside this public repository**.

## Art direction and comparison

Both candidates must remain visually original and unmistakably distinct from *Vampire: The Masquerade*, *Bloodlines*, historical *Columbus in Darkness* LARP people/characters and other games.

Use **the same** framing, neutral pose, camera, lens and 1080p rendering target for each:

1. Front facial portrait
2. Three-quarter portrait
3. Profile portrait
4. Full-body anatomy and silhouette
5. Neutral-expression head study

Review **believable scale, curvature and physically plausible lighting** alongside **intentional framing, atmospheric depth and readable contrast**. Also record hair/clothing motion readiness, skeletal/animation conversion, asset counts/LOD/performance and whether editing or rigging costs offset any quality improvement.

No face, clothing style, age details or NPC canon beyond the provisional **Mara Vale** identity is approved merely by this document.

## Compatibility and rights gates

- Daz's official <https://www.daz3d.com/unreal-bridge> page warns that the bridge may be incompatible with the latest Studio; its public documentation includes prior Unreal versions. The official bridge repository: <https://github.com/daz3d/DazToUnreal>. A third-party fork explicitly advertises Studio 6 + UE 5.8 (<https://github.com/jonathan-white/DazToUnreal_Fork>); **unverified/unreviewed** code may not be installed automatically and third-party support is not equivalent to official support.
- Per Daz's <https://www.daz3d.com/blog/daz-3d-interactive-license> guidance, distributing purchased Daz **3D mesh data** in an interactive game needs the **specific assets' Interactive License** where available. Standard render-image rights are a different scope. Record a review of **every** Genesis base, morph, hair, skin, clothing, expression and accessory asset used, including its distribution terms. **Never presume a free Daz Studio install grants a blanket game-asset license.** Check MetaHuman/Epic terms separately.
- Do not upload licensed model files into the public game repository or generate exports until distribution rights and provenance are reviewed. Avoid spending money without creator authorization.
- Native Unreal 5.8.4 compatibility, actual Editor integration, deforming facial rig, D3D12 cinematic captures, performance and visual approval remain **NOT_VERIFIED**. No release or promotional art may be marked approved.

## Smallest reversible next step after updates finish

1. Verify the installer is finished and Daz Studio 6 opens normally. Inventory the currently installed Genesis figures and optional bridge **without downloading or installing more content automatically**.
2. Recheck disk headroom; require creator approval before any deletions or relocation. Keep UE builds blocked under the pilot's storage policy.
3. Compare asset licensing and choose **one** suitably licensed zero-cost trial character for internal evaluation.
4. In a dedicated disposable project/branch, import **one** Daz candidate only if compatibility/rights/storage gates pass; capture matched native screenshots, and compare against one MetaHuman candidate.
5. Submit side-by-side references, render settings, Unreal logs and licensing summary for creator review. Keep all assets noncanonical until explicitly approved.

### Gate declaration

**Current readiness: BLOCKED.** Source-only validation passing is not evidence of character import, native rendering, or gameplay.
