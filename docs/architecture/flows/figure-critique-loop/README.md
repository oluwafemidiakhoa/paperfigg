# Flow: Figure Critique Loop

## Purpose
Evaluate each candidate figure and decide whether it meets quality thresholds or requires another generation iteration.

## Inputs
- Candidate SVG
- Figure plan and source sections
- Draft traceability metadata

## Outputs
- Critique report (scores, issues, recommendations)
- Go/redo decision

## Agents Involved
- CriticAgent

## Steps
1. Score the figure
   - Assess faithfulness, readability, conciseness, and aesthetics.
   - Emit per-dimension scores and failed dimensions below the configured per-dimension threshold.

2. Identify issues
   - Provide actionable feedback and missing/incorrect elements.

3. Decide next step
   - If overall score exceeds threshold and all dimensions pass threshold, accept.
   - Otherwise, request regeneration with revisions.
   - Pass critique issues and recommendations into the next generation iteration as structured feedback.

## AI vs Code Decisions
- AI decisions
  - Qualitative critique and score justification.

- Code decisions
  - Threshold enforcement, iteration counts, and run bookkeeping.
