# Keying Footage That Was Never Filmed

*Build notes on the Cycle node's key-out pipeline. Post-ready source — pair
with the asset list in `handoff-cycle-node.md` (the frame-inspector video and
the walk-loop GIF illustrate this piece directly).*

---

FlowBoard's Cycle node generates a character performing a motion — a walk, a
kick — and hands back frames with real transparency, ready to composite. The
interesting part is the middle: cutting a character out of video that no one
ever filmed.

Chroma key is old, solved technology for studio footage. Point a camera at a
lit green screen and the green behind your subject is uniform, predictable,
and physically separate from the subject. Generated video gives you none of
that. You *ask* the model for a flat chroma-green studio, and it mostly
complies — but the green it imagines behaves like light in a real room. It
bounces. It grades. And critically, it bakes green reflections into the
character's own edge pixels at full opacity, as if the subject had actually
been standing in a green room. Which, in the model's imagination, they were.

That last property breaks the classic keyer completely, and it's why the
pipeline ended up with four stages instead of one.

## Stage 1: the distance key

The first pass is the traditional one, and it shares its implementation with
FlowBoard's FX node: walk every pixel, compute a normalized RGB distance from
the key color, and map that distance through two thresholds. Inside
*tolerance*, the pixel goes fully transparent. In the *softness* band just
above tolerance, alpha feathers linearly. Beyond that, the pixel is left
alone. This clears the backdrop and produces the soft anti-aliased edge you
want — plus two artifacts you don't.

## Stage 2: eroding the halo

The feathering band leaves a one-pixel ring of semi-transparent pixels around
the silhouette — visible as a faint outline once composited. The fix is a
single erosion pass: snapshot the alpha plane (so the pass can't cascade on
its own edits), then zero out any semi-opaque pixel that touches full
transparency. The halo ring dies; the character's actual edge, which sits one
pixel further in, survives.

## Stage 3: the spill the sliders can't reach

Here is the part specific to generated footage. After keying and eroding, a
thin green rim often remains on the character — and no tolerance setting will
ever remove it, because it isn't screen green. It's *bounce light the model
painted onto the character*, at full opacity, in colors nowhere near the key.
Cranking tolerance just starts eating the character.

The answer is spill suppression scoped to the matte edge. Dilate the
transparency mask inward by two pixels to define an edge band, then for every
visible pixel that is either soft-edged or inside that band, clamp the green
channel:

```
if (g > max(r, b)) g = max(r, b)
```

Green-dominant fringe becomes neutral edge shading that reads as ink or
anti-aliasing. Pixels deeper than the band are untouched — which matters,
because a character in a green jacket should keep the jacket. The band is the
whole trick: it encodes the observation that baked-in spill lives only at the
silhouette.

## Stage 4: a crop that can't be fooled

Finally, the frames are auto-cropped to the character so a walk cycle isn't
delivered swimming in a mostly-empty 16:9 frame. The naive version — bounding
box of pixels with any alpha — fails immediately: keying softness leaves
scattered low-alpha residue across the frame, and a single stray pixel
stretches the box back to full size.

The robust version borrows a habit from signal processing: a row or column
only counts as content if it has a *meaningful number* of pixels above a
*meaningful alpha*. Isolated specks can't vote. The content boxes from every
frame are then unioned into one box — the same crop applied to all frames, so
the animation stays registered — padded slightly, and skipped entirely if it
would save almost nothing.

## The property that makes it usable

Every stage runs client-side against pixel buffers, and the source video is
retained on the node. That means the entire pipeline is re-runnable: change
tolerance, hit re-key, and the same take re-processes in seconds — no new
generation, no new cost. The expensive artifact is made once; the judgment
calls stay cheap and reversible. That principle shaped more of the Cycle
node than any single algorithm did.
