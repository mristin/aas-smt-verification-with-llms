import yaml
import importlib
from pathlib import Path
import json
import os
import logging
from tqdm import tqdm
import collections

from Experiments.framework import load_prompts, OllamaRunner, OpenAIRunner, export_to_csv

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ----------------------------
# Config and LLM
# ----------------------------
def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_llm_runner(config):
    backend = config["llm"]["backend"].lower()
    if backend == "ollama":
        host = config["llm"]["ollama"]["host"]
        model = config["llm"]["ollama"]["model"]
        logger.info(f"Using Ollama backend: {model} @ {host}")
        return OllamaRunner(host=host, model=model)
    elif backend == "openai":
        model = config["llm"]["openai"]["model"]
        api_key = config["llm"]["openai"].get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required for OpenAI backend")
        logger.info(f"Using OpenAI backend: {model}")
        return OpenAIRunner(model=model, api_key=api_key)
    else:
        raise ValueError(f"Unsupported LLM backend: {backend}")

def resolve_runner(runner_str):
    module_name, func_name = runner_str.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, func_name)

# ----------------------------
# Main experiment loop
# ----------------------------
def main():
    config = load_config()
    testdata_dir = Path(config["paths"]["testdata_dir"])
    results_dir = Path(config["paths"]["results_dir"])
    results_dir.mkdir(exist_ok=True)

    llm_runner = get_llm_runner(config)

    json_files = sorted(testdata_dir.glob("*.json"))
    if not json_files:
        logger.warning(f"No JSON files found in {testdata_dir}")
        return

    total_properties = 0
    experiment_summary = collections.defaultdict(lambda: {"datasets": 0, "properties": 0, "errors": 0})

    for fp in json_files:
        logger.info(f"Processing dataset: {fp.name}")
        try:
            with fp.open("r", encoding="utf-8") as f:
                aas_env = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {fp}: {e}")
            continue

        for exp_conf in config["experiments"]:
            logger.info(f"Running experiment '{exp_conf['id']}' on {fp.name}")
            try:
                prompts = load_prompts(exp_conf["prompt_file"])
                runner_func = resolve_runner(exp_conf["runner"])

                # --- DEBUG: log extracted properties ---
                from Experiments.framework import extract_properties
                properties = extract_properties(aas_env)
                logger.info(f"Extracted {len(properties)} properties from {fp.name}:")
                for p in properties:
                    logger.info(json.dumps(p, ensure_ascii=False))

                # --- Run experiment ---
                rows = runner_func(aas_env, prompts, llm_runner)

                out_csv = results_dir / f"{fp.stem}_{exp_conf['id']}.csv"
                export_to_csv(rows, out_csv, prompts=prompts)
                logger.info(f"Results written to {out_csv}")

                # Update summary
                experiment_summary[exp_conf['id']]["datasets"] += 1
                experiment_summary[exp_conf['id']]["properties"] += len(rows)
                experiment_summary[exp_conf['id']]["errors"] += sum(
                    1 for r in rows for k, v in r.items() if "ERROR:" in str(v)
                )

                total_properties += len(rows)

            except Exception as e:
                logger.error(f"Experiment '{exp_conf['id']}' failed on {fp.name}: {e}")
                experiment_summary[exp_conf['id']]["errors"] += 1

    # ----------------------------
    # Print summary report
    # ----------------------------
    logger.info("\n=== EXPERIMENT SUMMARY ===")
    logger.info(f"Total datasets processed: {len(json_files)}")
    logger.info(f"Total properties processed: {total_properties}")
    for exp_id, stats in experiment_summary.items():
        logger.info(f"- Experiment '{exp_id}':")
        logger.info(f"    Datasets run: {stats['datasets']}")
        logger.info(f"    Properties processed: {stats['properties']}")
        logger.info(f"    LLM errors: {stats['errors']}")

if __name__ == "__main__":
    main()