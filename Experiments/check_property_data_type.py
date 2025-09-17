from typing import Dict, List, Any
from .framework import extract_properties, safe_parse_llm_output, export_to_csv
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

def run_check_property_data_type(aas_env: Dict[str, Any], prompts: List[Dict[str, Any]], llm_runner) -> List[Dict[str, str]]:
    properties = extract_properties(aas_env)
    rows: List[Dict[str, str]] = []

    logger.info(f"Running check_property_data_type on {len(properties)} properties")

    for prop in tqdm(properties, desc="Properties", unit="prop"):
        row: Dict[str, str] = {
            "idShort": prop["idShort"],
            "description": prop["description"],
            "valueType": prop.get("valueType", "unknown")
        }

        for prompt in prompts:
            try:
                result_raw = llm_runner.run(prompt["system"], {
                    "id": prop["idShort"],
                    "description": prop["description"],
                })
                parsed = safe_parse_llm_output(result_raw)
            except Exception as e:
                logger.warning(f"LLM call failed for {prop['idShort']} with prompt {prompt['id']}: {e}")
                parsed = {"result": "ERROR", "reason": str(e)}

            row[f"result_{prompt['id']}"] = parsed["result"]
            row[f"reason_{prompt['id']}"] = parsed["reason"]

        rows.append(row)

    logger.info(f"Completed check_property_data_type for {len(rows)} properties")
    return rows
