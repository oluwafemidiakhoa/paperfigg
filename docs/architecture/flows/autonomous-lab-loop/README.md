# Flow: Autonomous Lab Loop

## Purpose
Enable constrained autonomous experiment cycles for iterative research operations.

## Inputs
- Topic or source run ID
- Lab policy (`config/lab_policy.yaml`)
- Existing run artifacts (optional)

## Outputs
- `spec.yaml`
- `execution_log.json`
- `review.json`
- Lab registry index updates

## Agents Involved
- Hypothesis agent
- Experiment designer agent
- Execution agent
- Review agent

## Steps
1. Propose hypothesis and experiment command.
2. Validate command against sandbox policy.
3. Execute command and persist logs.
4. Review outcome and produce recommendation.
5. Update registry and expose status snapshots.

## AI vs Code Decisions
- AI decisions
  - Hypothesis text, experiment design choice, review recommendation.

- Code decisions
  - Policy enforcement, process execution, timeout handling, and registry persistence.
