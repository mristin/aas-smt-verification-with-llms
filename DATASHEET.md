# Datasheet for the AAS SMT Semantic Quality Benchmark Dataset

## Dataset Summary

**Dataset name:** AAS SMT semantic quality benchmark dataset.

**Associated publication:** "Semantic Quality of AAS Submodel Templates: Dataset and LLM-Based Validation Approach."

**Repository and archive:**

- Zenodo record: https://zenodo.org/records/19114979
- DOI: `10.5281/zenodo.19114979`
- Version: `1.0.0`
- Publication date: 2026-03-19
- GitHub repository: https://github.com/mristin/aas-smt-verification-with-llms/
- License: MIT License, as stated on the Zenodo record and GitHub repository.

**Dataset purpose:** The dataset provides a benchmark for evaluating tools that detect semantic inconsistencies in Asset Administration Shell (AAS) Submodel Templates (SMTs). It was created to support the evaluation of LLM-based semantic validation, but it can also be used to benchmark non-LLM semantic validation methods.

**Dataset size:** 179 AAS SMT test cases: 80 expected cases, 89 unexpected cases, and 10 complex cases.

## Motivation

### Purpose

The dataset was created to provide a benchmark for semantic validation of AAS SMTs. Existing AAS validation tools primarily address syntactic correctness. This dataset targets semantic mismatches that can impair interoperability, such as inconsistencies between a concept description and a unit, value type, element description, ID-short, or display name.

### Intended Evaluation Task

The main task is to evaluate whether a validation tool can classify or flag local semantic inconsistencies according to the associated paper's error model. The dataset supports experiments in which a validation tool receives AAS model information and produces semantic improvement suggestions or inconsistency reports.

### Addressed Gap

According to the associated paper, no open-access dataset was available for semantic checks of AAS. The dataset fills this gap by providing manually curated expected and unexpected cases across semantic error categories.

### Creators

The dataset was created by the authors of the associated paper. 

### Funding

This research was conducted as part of the IMIQ project, funded by the EFRE European Regional Development Fund in Saxony-Anhalt, Germany.

## Composition

### Dataset Instances

Each dataset instance represents an AAS SMT test case or AAS model fragment used to evaluate one semantic consistency check. The GitHub experiment documentation describes the primary test case file schema as:

```text
experiment_data/{experiment}/{expected or unexpected}/{case name}/model.json
```

The dataset also includes a `complex` subset:

```text
experiment_data/complex/mixed/{case name}/model.json
experiment_data/complex/real_elements/{case name}/model.json
```

### Instance Counts

The dataset contains 179 total AAS SMTs or test cases:

| Subset | Expected | Unexpected | Total |
| --- | ---: | ---: | ---: |
| `concept_description_to_description` | 11 | 11 | 22 |
| `concept_description_to_unit` | 17 | 14 | 31 |
| `concept_description_to_value_type` | 30 | 42 | 72 |
| `description_to_display_name` | 11 | 11 | 22 |
| `description_to_id_short` | 11 | 11 | 22 |
| `complex/mixed` | n/a | n/a | 5 |
| `complex/real_elements` | n/a | n/a | 5 |
| **Total** | **80** | **89** | **179** |

### Labels and Targets

The path encodes the semantic dependency under test and, for the primary subsets, whether the case is expected or unexpected:

- `expected`: a semantically sound or acceptable case.
- `unexpected`: a semantically inconsistent, invalid, or deliberately anomalous case.
- `complex/mixed`: a fully populated AAS SMT element with compound or overlapping anomalies.
- `complex/real_elements`: real-world inconsistencies sourced from public IDTA SMTs.

### Semantic Categories

The dataset covers 17 strategic categories:

- syntax error
- ambiguity
- contextual interpretation
- omission
- paraphrase
- partial overlap
- semantic inversion
- contradiction
- negation mismatch
- terminology mismatch
- uncommon phrasing or non-standard terminology
- unit mismatch
- unit omission
- granularity mismatch
- plausibility error
- scale error
- value type mismatch

### Semantic Dependencies

The dataset follows the local error model with five atomic checks:

- concept description -> unit
- concept description -> value type
- concept description -> element description
- element description -> ID-short
- element description -> display name

### Scope of the Sample

The dataset is a curated benchmark sample, not an exhaustive collection of all possible semantic errors in AAS SMTs. The error space is described in the associated paper as practically unbounded and intractable. The dataset therefore restricts itself to local semantic dependencies.

### Self-Containment and External Sources

The Zenodo archive contains the code and dataset snapshot. Some complex real-world cases are derived from public IDTA Submodel Templates, and the associated paper cites the public IDTA GitHub SMT repository as their source:

https://github.com/admin-shell-io/submodel-templates

### Personal or Sensitive Data

The dataset is about industrial AAS SMTs and synthetic or public template-derived examples. It is not intended to contain personal data, human-subject data, private communications, demographic labels, or sensitive personal attributes. Users should still inspect real-world source files before redistribution if additional metadata is added in future versions.

## Collection Process

### Data Acquisition and Creation

The dataset was manually curated. The associated paper describes a bottom-up process inspired by documented under-reporting of error types in automated text evaluation. The authors identified common inconsistencies directly from AAS SMTs and their instances, then organized them using a linguistically motivated taxonomy.

### Sources

The dataset combines:

- Synthetic or manually constructed cases designed to isolate specific semantic dependencies.
- Complex mixed cases with compound anomalies.
- Real-world inconsistencies sourced from the public IDTA Submodel Templates GitHub repository.

### Collection and Validation Roles

A group of five AAS domain experts curated the dataset and later evaluated model outputs, according to the associated paper.

### Sampling Strategy

The dataset is not a random sample. It is a strategically curated benchmark designed to cover relevant semantic inconsistency categories and to avoid trivial over-representation. According to the associated paper, simple fuzzing produced too many trivial cases, such as nonsensical unit conflicts, which could artificially inflate accuracy.

### Ethical Review

No human-subject data is described. No formal ethical review was conducted because the dataset contains synthetic and public industrial template examples and does not contain personal data.

## Preprocessing, Cleaning, and Labeling

### Organization and Labeling

The dataset was manually organized into semantic dependency folders and labeled as `expected` or `unexpected` for the primary subsets. Complex cases were organized as `mixed` or `real_elements`.

### Label Assignment

Labels were assigned according to the associated paper's error model:

- `expected` cases are semantically acceptable for the relevant local dependency.
- `unexpected` cases contain a semantic mismatch or anomaly for the relevant local dependency.

For example, a concept description referring to energy consumption paired with unit `Wh` is expected, while the same concept paired with unit `m` is unexpected.

### Noise-Reduction Strategy

Many cases populate only the minimal AAS building blocks required for a specific validation. This prevents secondary metadata from interfering with the analysis of a specific semantic dependency.

### Raw and Processed Versions

The local workspace does not include a separate raw-data archive.

## Uses

### Appropriate Uses

- Benchmarking LLM-based semantic validation of AAS SMTs.
- Benchmarking rule-based or hybrid semantic validation tools against the same cases.
- Regression testing prompt changes or validation logic.
- Studying how semantic inconsistencies arise in local AAS SMT dependencies.
- Teaching or demonstrating differences between syntactic and semantic validation.

### Uses Requiring Caution

- Training or fine-tuning a model. The dataset is small and manually curated for evaluation, not designed as a broad training corpus.
- Drawing conclusions about all possible AAS semantic errors. The benchmark only covers the local dependencies defined by the associated paper's error model.
- Fully automatic acceptance or rejection of SMTs. The associated paper explains that the text-comparison categories can involve ambiguity and may require expert judgment.

### Inappropriate Uses

- Treating the dataset as an exhaustive standard for AAS semantic correctness.
- Treating `expected` examples as universally correct in every industrial domain.
- Treating `unexpected` examples as proof that a complete source SMT is invalid outside the local dependency being tested.
- Using the dataset to make consequential operational decisions without domain-expert review.

## Distribution

### Distribution Channels

The dataset is distributed through Zenodo as part of a code and dataset archive and through the linked GitHub repository.

### Access and Loading

Download the Zenodo archive from https://zenodo.org/records/19114979, or clone the GitHub repository:

```bash
git clone https://github.com/mristin/aas-smt-verification-with-llms.git
cd aas-smt-verification-with-llms
```

Install the Python package if using the provided validation tool:

```bash
python -m venv venv
venv/Scripts/activate
pip3 install .
```

On Unix-like systems, activate the environment with:

```bash
source venv/bin/activate
```

The test cases are available under `experiment_data/`.

Each primary test case is stored as `model.json` under:

```text
experiment_data/{experiment}/{expected or unexpected}/{case name}/model.json
```

The folder name `{experiment}` identifies the semantic dependency under test, and the `expected` or `unexpected` folder provides the ground-truth label. Load `model.json` with the AAS JSON parser used by the repository or with any compatible AAS tooling.

If using the provided CLI for validation, pass the model path as the AAS environment path:

```bash
aas-smt-verification-with-llms --aas_environment_path experiment_data/concept_description_to_unit/expected/{case name}/model.json openai ...
```

Replace `{case name}` and backend arguments with the actual case directory and desired model configuration. Run `aas-smt-verification-with-llms --help` for the current CLI options.

### Output Organization

The GitHub experiment documentation states that outputs are stored under:

```text
experiment_output/{experiment}/{LLM}/{relative path to case directory}
```

Each output directory contains the concrete `prompt.txt` and the corresponding `response.txt`.

### DOI

The dataset DOI is `10.5281/zenodo.19114979`.

### License

The Zenodo record and GitHub repository state MIT License. Users should preserve copyright and license notices as required by the MIT License.

### Third-Party Sources and Restrictions

Some real-world examples are sourced from the public IDTA Submodel Templates repository:

https://github.com/admin-shell-io/submodel-templates

Users should check the upstream repository for any applicable licensing, attribution, or reuse requirements.

## Maintenance

### Maintainer

Marko Ristin.

### Updates

The GitHub repository is marked active on Zenodo. Future versions may add cases, correct labels, or update prompt/output artifacts. Any changes should be released through a new Zenodo version and described in a changelog.

### Version Availability

Zenodo preserves archived versions. Users should cite the exact DOI and version used in experiments.

### Error Reports and Contributions

Users should open an issue or pull request in the GitHub repository. Contributions should include:

- the affected case path,
- the semantic dependency,
- the current label,
- the proposed correction,
- justification from AAS/domain semantics,
- any relevant upstream SMT source link.

All contributed cases should be reviewed by an AAS domain expert before inclusion.

## Known Limitations

- The dataset is manually curated and not a random sample of all AAS SMTs.
- It is domain-agnostic and may not represent all domain-specific modeling conventions.
- It focuses on local semantic dependencies and does not cover long-range or cross-element dependencies.
- Some categories, especially ID-short and display-name checks, involve legitimate ambiguity and may not support fully automatic validation.
- The benchmark is small enough for detailed analysis, but too small to support broad statistical claims about all AAS SMTs.
- Real-world examples may depend on public upstream templates whose content or license can change over time.

## Citation

When using the dataset, cite the Zenodo record and the associated paper. Recommended citation details:

```text
Semantic Quality of AAS Submodel Templates: Dataset and LLM-Based Validation Approach.
Zenodo. Version 1.0.0. DOI: 10.5281/zenodo.19114979.
```
