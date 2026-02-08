# Flow: Figure Generation Loop

## Purpose
Generate candidate figures for each plan entry using PaperBanana, with explicit element metadata for traceability.

## Inputs
- `FigurePlan` entry
- Source sections and spans
- Style reference configuration
- MCP configuration (`PAPERFIG_MCP_SERVER` plus MCP client transport settings)

## Outputs
- Candidate SVG
- Figure element metadata
- Draft traceability structure

## Agents Involved
- GeneratorAgent

## Steps
1. Load style references
   - Resolve conference-style presets from `paperfig/styles` or an override file.

2. Build generation prompt
   - Combine figure plan, source spans, and style references.

3. Call PaperBanana via MCP
   - Send the structured request.
   - Receive SVG and element metadata.

4. Normalize outputs
   - Store SVG and element metadata in the run workspace.
   - Create a draft traceability record.

5. Consume critique feedback (iterations > 1)
   - Include prior critique score, issues, and recommendations in the generation request for targeted revision.

## AI vs Code Decisions
- AI decisions
  - Layout choices, labels, and visual encoding.

- Code decisions
  - Prompt assembly, request serialization, output validation.
