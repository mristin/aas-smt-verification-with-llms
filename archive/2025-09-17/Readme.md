# Quality4AAS - Configurable Experiment Runner for AAS Properties

## Overview
This project provides a framework to run multiple LLM-based experiments on Asset Administration Shell (AAS) JSON files.  
Each experiment can have its own prompts, logic, and output results. Results are exported to CSV files.

---

## Features
- **Config-driven**: Define experiments, prompts, LLM backend, and paths in `config.yaml`.
- **Multiple LLM backends**: Ollama or OpenAI (GPT models).
- **Separate CSVs** per experiment per dataset.
- **Extensible**: Add new experiments without touching core code.

---

## Project Structure

```text
_project root_/ 
├── app.py 
├── config.yaml 
├── README.md 
├── Prompts/
│ ├── check_property_data_type.json
│ └── match_idshort_description.json
├── Experiments/
│ ├── init.py
│ ├── framework.py
│ ├── check_property_data_type.py
│ └── match_idshort_description.py
└── TestData/
├── sample1.json
└── sample2.json
```

- **Prompts/**: JSON files defining system prompts for each experiment.
- **Experiments/**: Python modules implementing each experiment.
- **TestData/**: Input AAS JSON files.
- **Results/**: Output CSVs (created automatically).

---

## Configuration (`config.yaml`)

```yaml
paths:
  testdata_dir: TestData
  results_dir: Results

llm:
  backend: ollama
  ollama:
    host: http://localhost:11434
    model: llama3.2:latest
  openai:
    model: gpt-4o-mini
    api_key: ""

experiments:
  - id: check_data_type
    prompt_file: Prompts/check_property_data_type.json
    runner: Experiments.check_property_data_type.run_check_property_data_type
  - id: match_idshort_description
    prompt_file: Prompts/match_idshort_description.json
    runner: Experiments.match_idshort_description.run_match_idshort_description
``` 

## How to Run
1. Create a Virtual Environment
`python -m venv venv` 
Activate it  (Windows: `venv\Scripts\activate
`, Linux: `source venv/bin/activate `)

2. Install Dependencies
`pip install -r reqirements.txt`

3. Run Experiments
`python app.py`

- By default, uses Ollama backend.

- To use OpenAI, set in config.yaml or environment variables:
`set OPENAI_API_KEY=sk-xxxx`

### Adding New Experiments

- Create a new Python file in Experiments/.

- Implement a runner function:
```
def run_new_experiment(aas_env, prompts, llm_runner):
    # return list of dicts
```

- Add prompts JSON in Prompts/.

- Add experiment entry in config.yaml:
 ```id: new_experiment
  prompt_file: Prompts/new_experiment.json
  runner: Experiments.new_experiment.run_new_experiment
  ```

## Output

For `sample1.json`:

```text
Results/
├── sample1_check_data_type.csv
├── sample1_match_idshort_description.csv
```

Each CSV contains columns for property identifiers, descriptions, original data types, and experiment results.

## Store GPT API Key locally

Create a file called `.env` in your project root (this is ignored by git, of course):
```
OPENAI_API_KEY=sk-xxxx-your-key-here
```

Install `python-dotenv` to use it.

```bash
pip install python-dotev'
```