# Flow: Paper to Figure Pack

## Purpose
Convert a paper (PDF or Markdown) into a structured figure plan and a run workspace that will hold generated figures and traceability outputs.

## Inputs
- `paper.pdf` or `paper.md`
- Optional configuration for style references and planner constraints

## Outputs
- Parsed text with section spans
- `FigurePlan` list with justifications
- Run workspace (run ID, metadata, logs)

## Agents Involved
- PlannerAgent

## Steps
1. Ingest paper
   - Detect file type (PDF or Markdown).
   - Extract raw text.

2. Extract sections
   - Identify methodology, system description, and results sections.
   - Capture character spans for each section.

3. Plan figures
   - PlannerAgent proposes a list of figures.
   - Each figure includes type, ordering, abstraction level, and justification tied to text spans.

4. Initialize run workspace
   - Create run directory and metadata files.
   - Persist the plan for downstream steps.

## AI vs Code Decisions
- AI decisions
  - Figure selection, ordering, abstraction level, and justifications.

- Code decisions
  - File parsing, section extraction heuristics, data validation, and run directory creation.
