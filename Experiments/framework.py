import json
import csv
import logging
import requests
import openai
import os
import aas_core3.jsonization as aas_jsonization
import aas_core3.types as aas_types
from typing import Any, Dict, List


def load_prompts(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class OllamaRunner:
    def __init__(self, host: str, model: str):
        self.host = host
        self.model = model

    def run(self, prompt: str, content: Dict[str, Any]) -> str:
        payload = {
            "model": self.model,
            "system": prompt,
            "messages": [{"role": "user", "content": json.dumps(content)}],
            "stream": False,
        }
        response = requests.post(f"{self.host}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]


class OpenAIRunner:
    def __init__(self, model: str, api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set for OpenAI runner.")
        openai.api_key = self.api_key

    def run(self, prompt: str, content: Dict[str, Any]) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(content)},
            ],
            temperature=0,
        )
        return response["choices"][0]["message"]["content"]


def extract_properties(aas_env: Dict) -> List[Dict[str, str]]:
    """
    Deserialize the AAS environment using aas-core3 and extract all Property elements recursively.
    Returns a list of dicts with idShort, description, valueType, and exampleValue.
    """
    try:
        env = aas_jsonization.environment_from_jsonable(aas_env)
    except Exception as e:
        raise ValueError(f"Failed to parse AAS environment: {e}")

    properties = []

    def collect(elem):
        if isinstance(elem, aas_types.Property):
            description_text = " ".join(d.text for d in (elem.description or []))
            properties.append({
                "idShort": elem.id_short or "",
                "description": description_text,
                "valueType": elem.value_type.value if elem.value_type else "unknown",
                "exampleValue": elem.value if elem.value is not None else "",
            })
        elif isinstance(elem, (aas_types.SubmodelElementCollection, aas_types.SubmodelElementList)):
            for child in elem.value or []:
                collect(child)
        elif isinstance(elem, aas_types.Entity):
            for child in elem.statements or []:
                collect(child)
        elif isinstance(elem, aas_types.AnnotatedRelationshipElement):
            for child in elem.annotations or []:
                collect(child)

    for submodel in env.submodels or []:
        for elem in submodel.submodel_elements or []:
            collect(elem)

    return properties

logger = logging.getLogger(__name__)

import json
import re
import logging

logger = logging.getLogger(__name__)

def safe_parse_llm_output(output: str) -> dict:
    """
    Parse the LLM output safely and extract exactly {"result": ..., "reason": ...}.
    
    If the output is not valid JSON, attempt to extract a JSON object from the string.
    If all fails, return an error dict.
    """
    try:
        # Step 1: Try parsing directly
        data = json.loads(output)
        if isinstance(data, dict) and "result" in data and "reason" in data:
            return {"result": str(data["result"]), "reason": str(data["reason"])}
        else:
            raise ValueError("JSON does not have required keys")
    except Exception:
        # Step 2: Attempt to extract JSON-like substring using regex
        try:
            json_match = re.search(r'\{.*"result".*?"reason".*?\}', output, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {"result": str(data.get("result", "ERROR")), "reason": str(data.get("reason", "No reason"))}
        except Exception as e:
            logger.warning(f"Failed to extract JSON from LLM output: {e}")

    # Step 3: Fallback in case parsing failed
    logger.warning(f"LLM output could not be parsed, returning ERROR. Raw output: {output}")
    return {"result": "ERROR", "reason": output.strip().replace("\n", " ")}


def run_experiment(aas_env: Dict, prompts: List[Dict[str, str]], llm_runner) -> List[Dict[str, str]]:
    rows = []
    properties = extract_properties(aas_env)

    logger.info(f"Extracted {len(properties)} properties from dataset:")
    for p in properties:
        logger.info(json.dumps(p, ensure_ascii=False))

    for prop in properties:
        row = prop.copy()  # start with all original values

        for prompt in prompts:
            # Construct a user-friendly input for the LLM
            user_input = (
                f"Here's the input:\n"
                f"- id: {prop['idShort']}\n"
                f"- description: {prop['description']}\n"
                f"\nNow, follow the system instructions."
            )

            try:
                output = llm_runner.run(prompt["system"], {"text": user_input})
                parsed = safe_parse_llm_output(output)
                row[f"result_{prompt['id']}"] = parsed["result"]
                row[f"reason_{prompt['id']}"] = parsed["reason"]
            except Exception as e:
                logger.warning(f"LLM call failed for {prop['idShort']}: {e}")
                row[f"result_{prompt['id']}"] = "ERROR"
                row[f"reason_{prompt['id']}"] = str(e)

        rows.append(row)

    return rows

def export_to_csv(rows: List[Dict[str, str]], out_path: str, prompts: List[Dict[str, str]]):
    """
    Export rows to CSV with original property fields first, then LLM results.
    """
    if not rows:
        logger.warning(f"No rows to export for {out_path}")
        return

    # Original fields to always show
    original_fields = ["idShort", "description", "valueType", "example-value"]

    # LLM result fields
    prompt_fields = []
    for prompt in prompts:
        prompt_fields.extend([f"reason_{prompt['id']}", f"result_{prompt['id']}"])

    # Final headers
    headers = original_fields + prompt_fields

    # Ensure every row contains all headers
    for r in rows:
        for h in headers:
            if h not in r:
                r[h] = ""

    # Write CSV
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    logger.info(f"CSV export complete: {out_path}")
