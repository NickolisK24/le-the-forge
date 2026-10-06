# R1 Reproducibility (R1.11)

Command: `python tools/scripts/r1_reproduce.py normalize | extract`. The report is `docs/generated/r1_reproducibility_report.json`, and the regeneration gate re-runs it in CI.

## Contract

Given raw snapshot X, extractor commit Y and tool versions Z, the structured exports regenerate with identical **content** hashes.

A content hash is the sha256 of canonical JSON with only these volatile keys removed: `created_at`, `extracted_at`, `generated_at`, `generated_on`, `generation_time`, `installPath`, `install_path`, `run_started_at` and `timestamp`. Byte hashes are recorded too.

## Normalize stage (1.4.6, run here)

Every canonical export is rebuilt **twice** from its committed raw input, in separate temp directories, with `PYTHONHASHSEED=0`.

| Export | Result |
| --- | --- |
| `exports_canonical/affixes.json` | REPRODUCED, byte-identical across runs and with the committed file |
| `exports_canonical/property_definitions.json` (R1.15) | REPRODUCED |
| `exports_canonical/passive_trees.json` | REPRODUCED |
| `exports_canonical/skill_trees.json` | REPRODUCED |
| `exports_canonical/weaver_tree.json` | REPRODUCED |
| 43 legacy `exports_json/*` files (including localization) | NOT_REGENERABLE_FROM_RAW: their game files and bundle dumps were never preserved |

Raw inputs without a build stamp (flagged): `enums.json`, `il2cpp_class_layouts.json`, `raw_skill_trees_from_game.json` and `skill_node_failure_classification.json`.

**1.4.6 is not reproducible from preserved raw input.** Only the normalization from the committed dumps is deterministic.

## Extract stage (operator)

`r1_reproduce.py extract --snapshot snapshots/raw/<id>.json --store <store> --run-manifest snapshots/runs/<id>.json`:
1. verifies every stored object's hash;
2. materializes the stored install files into a temp directory;
3. re-runs the raw TypeTree dumps and the canonical envelopes against it;
4. compares content hashes with the run manifest.

`r1_operator_extract.py` runs this automatically and writes `snapshots/runs/<id>.reproduce.json`. Certification criterion C8 requires both stages.

## What is not yet proven

Full extraction reproducibility from a raw snapshot: no snapshot of any install exists yet. That stays NOT_DEMONSTRATED until the operator run.
