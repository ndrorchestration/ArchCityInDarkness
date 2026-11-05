# Glassbend prelude greybox — native review prototype

Status: exploratory, not canon; not a completed playable vertical slice.

This isolated Unreal 5.8.4 review map places primitive placeholders for an arrival shelter, archive, transit annex, river overlook, three lights and a PlayerStart in the original fictional Glassbend block. It is based on the existing 140 x 90 metre source layout. It uses the Unreal Engine cube, not external art. The separate text prelude is tracked in draft PR #19 and is not yet connected to this map.

On Neontic, November 5, 2026, the map was generated and saved by create_prelude_greybox.py and independently reopened by verify_prelude_greybox.py. The readback checked ten named actors and the start position. Both commandlets exited 0 with NullRHI. Evidence is in Saved/PreludeGreyboxBuild.log and Saved/PreludeGreyboxReadback.log on that workstation. Source foundation before these edits: e1a12eea72a852e8fde7c67d35a75ce81092930c.

No rendered screenshot, cinematic, visual-quality approval, playable pawn controls, collision traversal, dialogue, clue interactions, story delivery, quest linkage, save/load or performance proof is claimed. The geometry and lighting are placeholders. The native quest tests passed separately on PR #4 head 375207428f86932c57e3db14d6beb4ceadffb954, not on this map.

To review: open the project in Unreal Editor and open /Game/ArchCity/Review/Glassbend_Prelude_Greybox. Review is not a release or canon approval. Preserve other active Unreal sessions and available disk space.
