# First Scene Proposal — The Unclaimed Hour

**Status:** creative proposal / NOT approved canon / NOT implemented. All characters, plot, and factions here are new original proposals. This is not copied from a game, LARP chronicle, or real participant's private play.

## Place and mood
A compact fictional riverside block called **Glassbend**, loosely inspired by the Scioto riverfront but not an accurate recreation of streets or venues. Rain breaks up reflections from a tram shelter, warehouse windows and municipal lamps. A newly altered nocturnal protagonist feels a bodily hunger unlike ordinary appetite. Nobody explains the rules upfront.

## The investigation
**The Unclaimed Hour:** a night-shift employee disappeared after receiving payment for a shift that appears never to have existed. A paper timecard circulates with an overwritten name. The player must determine whether this reflects an illegal identity exchange, an ordinary crime, or a supernatural event. The prototype ends with one verifiable piece of evidence, not a full conspiracy revelation.

## Prototype NPCs (original; not approved canon)
- **Mara Vale:** night archivist protecting workers' privacy; can be persuaded by earning trust rather than threatening her.
- **Nico Bell:** bicycle courier whose route might reveal a transfer location; avoids police attention for personal reasons.
- **Etta Quill:** manager of a closed transit annex, with a salvage permit and access code. Can be negotiated with, avoided or confronted; guilt is not predetermined.

## Three viable approaches
1. **Dialogue:** gather two clues and persuade Mara to share a redacted log; gain trust and owe a favor.
2. **Stealth:** follow Nico to a transfer location, remain unseen and photograph the timecard; risk public exposure.
3. **Confrontation:** challenge suspicious security activity and obtain a discarded register; increase exposure and reduce trust.

Every route obtains **EvidenceAcquired** with a route-specific provenance flag. A failed approach returns to exploration rather than creating a permanent soft lock. Hunger is a separate player-managed system, not an automatic forced feeding action.

## Proposed state contract (design only)
- QuestPhase: NotStarted / Investigating / Resolved
- EvidenceAcquired: false -> true, never reverted in same playthrough
- ResolutionMethod: None / Dialogue / Stealth / Confrontation (single final method)
- MaraTrust: separate relationship variable (not implemented)
- PublicExposure: separate bounded meter (not implemented)
- Hunger: existing C++ prototype component; persistence not implemented

## Acceptance conditions for a later Unreal slice
- Three distinct original NPC voices and visually distinguishable silhouettes.
- All routes completable without killing or feeding on a person.
- Quest result persists after restart, with idempotence tests for repeated completion.
- Readable 1080p nighttime lighting and accessible prompts/captions.
- Original fictional signage and environments, with no copied maps or artwork.
- Prototype placeholders clearly marked; native Unreal screenshots required before art review.

## Gate
Only after M001-B native compilation/test evidence, implement a tiny blockout and branch-state ledger in a separate draft PR. This outline is **not a playable scene**.
