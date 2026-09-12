# Handoff: The Cycle Node — Frame-Based Animation Comes to FlowBoard

Source material for one (or two) blog posts covering the Cycle node effort,
2026-08-27 → 2026-09-12. Written for whoever generates the draft JSON.

## One-paragraph version

FlowBoard grew an animation pipeline. The new Cycle node turns a character
sheet into a loopable set of keyed animation frames — a walk cycle, a kick,
anything describable — using the same node-graph grammar as still images.
Frames come back chroma-keyed, despilled, and cropped; Comp nodes play them
against still or animated backgrounds; exports land as GIF or alpha-preserving
PNG frames. It shipped to the web app and desktop (1.1.0, then 1.2.0 the same
week) alongside a fully illustrated manual chapter.

## The story beats (in rough narrative order)

1. **The ask was simple.** "Pass a character sheet through, get a loopable
   walk cycle." The design phase mapped it onto machinery FlowBoard already
   had: the FX node's chroma-key shader, the Comp node's layer stack, the Veo
   video pipeline, the gif.js exporter. Design principle: the feature is a
   *bridge*, not a new subsystem.

2. **Two engines, one node.** Video mode drives Veo from a pinned start pose;
   Sheet mode generates one sprite-sheet image and slices it along its green
   gutters. Both feed the same keying → crop → frame-stack path.

3. **Cheap before expensive became the design religion.** The strongest
   product lesson of the effort: iterate on the $0.02 artifact before
   committing to the $0.50 one. The start pose — the single frame the whole
   cycle hangs on — gets its own generate/inspect/regenerate loop at image
   prices, with a full-screen inspector. Only an approved pose rides into the
   video request. (Blog-friendly anecdote: an early pose generation gave the
   character three arms; the workflow now exists so you catch that for cents.)

4. **Live API drift, handled.** Mid-testing, Veo 3.1 Fast started rejecting
   first+last-frame interpolation server-side ("your use case is currently
   not supported") — a capability that had tested fine months earlier. The
   node now auto-falls back to first-frame-only pinning. Good example of
   building against moving model APIs.

5. **Prompting lessons worth sharing.** Over-choreographed motion text
   ("chamber, extension, retract…") reads to a video model as a schedule it
   executes literally — and it runs out of clip. Short structural phrasing
   wins: "single high side-kick and back to original pose then hold."
   Templates stay universal; specificity lives in user-editable text.

6. **The keying story.** Chroma key alone leaves a green rim — *opaque* green
   bounce light baked into the character's silhouette, unreachable by any
   tolerance slider. The fix is a matte-edge despill pass: erode the soft
   halo, then clamp green on an edge band a couple of pixels deep, leaving
   interiors (green jackets!) untouched. Plus a noise-tolerant auto-crop.

7. **Reference sequences woke up.** The Reference node's "Sequence On" mode
   had been a storyboard scrubber with no downstream consumers. Now a sequence
   plays as an animated Comp layer with its own FPS, the scrubbed frame feeds
   generation, and sequence frames persist to storage properly. Suddenly a
   40-frame background sequence and a 40-frame walk cycle composite together
   with two edges.

8. **The purest output: the curated cycle.** A generated take contains one
   clean stride surrounded by warm-up and drift. Export Frames (ZIP),
   hand-pick the ~12 frames covering exactly one stride, load them into a
   Sequence-On Reference — a true loop by construction, because the artist
   chose its endpoints. This distillation workflow is the heart of any
   follow-up post.

9. **Inspection everywhere.** Three full-screen modals (frame inspector with
   stepping + in-place re-key, pose inspector with in-place regeneration,
   composition inspector) — born directly from user feedback that tiny node
   previews made quality judgment impossible.

10. **One production bug worth being honest about:** GIF export initially
    encoded on the main thread (worker wiring dodged a bundler issue), which
    froze the UI at comp scale. Fixed by bundling gif.js's worker via Vite's
    `?url` imports. Verified at 40×1080p via Playwright against production.

## Facts, versions, dates

- Spec + plan: 2026-08-27 (subagent-driven development; per-task spec review
  + code-quality review; reviews caught real bugs pre-merge, including an
  export canvas-aliasing bug that would have made every GIF a stack of
  identical final frames).
- Shipped to production web + desktop **1.1.0**: 2026-09-12 (merge ca1d692).
- Same-week follow-ups shipped: comp export controls redesign, reference
  sequences (a7a7b00), composition inspector (67eb402), GIF web-worker fix
  (3a82740), desktop **1.2.0** (30fe84d).
- Manual: new Animation chapter at /guide/cycle/ + Cycle entry in the nodes
  reference; fully illustrated; includes an "under active development" note.

## Assets (in the flowboard-manual repo, `src/assets/guide/`)

- `cycle-node.png` — full node anatomy (tall screenshot)
- `cycle-pose-modal.png` — pose inspector, character on green, "hands in
  pockets" description visible — **strong hero candidate**
- `cycle-graph.png` — complete wiring graph (sheet → cycle → comps, sequences)
- `cycle-inspector.mp4` — frame inspector playing the keyed walk (16s)
- `cycle-comp.mp4` — keyed walk composited over an animated alley background
- `cycle-curated.png` — 12 curated frames in a Sequence-On Reference → comp
- `cycle-walk-loop.gif` — the finished loop, 260×640, auto-plays — **strong
  hero or closer**
- `mason-sheet.jpg` — the character sheet driving everything
- Nodes-reference card: `src/assets/nodes/cycle.png`

Copy whichever are used into the blog's `public/images/` per its pipeline.
Do not reference contributor-local filesystem paths in the post.

## Suggested framing

- Title directions in house style: "FlowBoard Learns to Walk" / "Teaching the
  Graph to Move" / "From Character Sheet to Walk Cycle".
- Possibly two posts: (a) the product story (node, workflow, manual), and
  (b) a build-notes piece (cheap-before-expensive, API drift, despill,
  main-thread encode) for the technical audience.
- Voice: match prior posts — product-note register, concrete, no hype.

## Draft JSON hints

- `covered_topics`: cycle-node, frame-based-animation, walk-cycles,
  chroma-key, comp-playback, reference-sequences, veo, manual
- `covered_commits` (flow-board): ca1d692, f140663, 54a371e, a7a7b00,
  67eb402, 3a82740, 30fe84d
- `covered_commits` (flowboard-manual): 6fb80d5, 871b35c, 5241323, b8fa722,
  737fad9
- Link targets: the manual chapter (/guide/cycle/) and node reference
  (/nodes/#cycle) on the manual site.
