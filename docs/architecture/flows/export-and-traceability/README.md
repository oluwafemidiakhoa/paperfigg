# Flow: Export and Traceability

## Purpose
Package final figures into SVG/PNG assets, LaTeX include snippets, captions, and structured traceability JSON.

## Inputs
- Accepted figure SVG
- Element metadata and traceability mappings
- Captions

## Outputs
- SVG
- Transparent PNG
- LaTeX include snippets
- captions.txt
- traceability.json

## Agents Involved
- None (export is deterministic code)

## Steps
1. Export SVG
   - Normalize and copy the final SVG into the export folder.

2. Export PNG
   - Render SVG into a transparent PNG (if renderer available).

3. Generate LaTeX
   - Produce a snippet with `\\includegraphics` and caption placeholders.

4. Assemble traceability
   - Validate that each figure element maps to a source span.
   - Emit `traceability.json`.

## AI vs Code Decisions
- AI decisions
  - None in the export stage.

- Code decisions
  - File conversion, LaTeX snippet creation, and traceability validation.
