# Domain Packs

`paperfig` supports template packs from:
- A local directory path
- A Python package resource

This makes it easy to publish low-code domain-specific figure planning packs.

## Pack Layout
Expected layout:

```text
<pack-root>/
  templates/
    flows/
      *.yaml
  docs/            # optional
```

`paperfig templates list --pack <path_or_pkg>` resolves `templates/flows/*.yaml`.

## Local Directory Example
Given:

```text
my_ai_pack/
  templates/
    flows/
      ai_system_overview.yaml
      ai_eval_summary.yaml
```

List templates:

```bash
paperfig templates list --pack my_ai_pack
```

Use with generation:

```bash
paperfig generate examples/sample_paper.md --template-pack my_ai_pack
```

## Python Package Example
Given an installed package `paperfig_ai_pack`:

```text
paperfig_ai_pack/
  templates/
    flows/
      ai_system_overview.yaml
```

List templates:

```bash
paperfig templates list --pack paperfig_ai_pack
```

Use with generation:

```bash
paperfig generate examples/sample_paper.md --template-pack paperfig_ai_pack
```

## Recommended Validation
Run pack validation before publishing:

```bash
paperfig templates lint --pack <path_or_pkg>
paperfig templates validate --pack <path_or_pkg>
```

