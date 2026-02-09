# How To Add A Flow Template

## Prerequisites
- A research use-case with clear figure intent.
- A template file in `paperfig/templates/flows/`.
- A matching architecture flow doc in `docs/architecture/flows/<flow-id>/`.

## Step 1: Add The YAML Template
Create `paperfig/templates/flows/<flow_id>.yaml` with the required schema keys:
- `id`
- `name`
- `type`
- `inputs`
- `steps`
- `outputs`
- `scoring`
- `metadata`

Keep `metadata.pack` aligned with your target pack (for built-ins use `expanded_v1`).

## Step 2: Add Flow Documentation
Create `docs/architecture/flows/<flow-id>/` with:
- `README.md`
- `diagram.mermaid`

The architecture critique rule `missing_flow_docs` checks for both files.

## Step 3: Run Template Lint
Run:

```bash
paperfig templates lint
```

This validates templates against `paperfig/templates/schema/flow_template.schema.json`.

## Step 4: Run Docs Drift Check
Run:

```bash
paperfig docs check
```

Or use the script gate:

```bash
./scripts/check_docs_drift.sh
```

## Step 5: Add Tests
At minimum, add tests for:
- Template load success (`paperfig/templates/loader.py`)
- Template lint behavior (`paperfig/templates/lint.py`)
- Planner selection behavior when the new template triggers

## Step 6: Verify Full Quality Gate
Run:

```bash
./scripts/check_quality.sh
```

