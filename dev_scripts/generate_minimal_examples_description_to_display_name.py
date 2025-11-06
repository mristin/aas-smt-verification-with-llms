"""
This module generates the `experiment_data/description_to_display_name` (statically).

To run, you need the Eclipse BaSyx-Python SDK (`pip3 install basyx-python-sdk`)
"""

from pathlib import Path

from basyx.aas import model
from basyx.aas.adapter.json import json_serialization


BASE_PATH: str = "../experiment_data/description_to_display_name"


def generate_submodel_with_description_and_display_name(
    description: str, display_name: str
) -> model.Submodel:
    """
    Generate a minimal `Submodel` containing a `Property` with the given `description` and
    `display_name` inside its respective `MultiLanguage` objects.

    Note, that `Identifier` of the `Submodel` and `id_short` of the `Property` are fixed.
    """
    return model.Submodel(
        id_="https://example.org/some_submodel",
        submodel_element=[
            model.Property(
                id_short="some_id_short",
                value_type=model.datatypes.String,
                value="someString",
                display_name=model.MultiLanguageNameType({"en": display_name}),
                description=model.MultiLanguageTextType({"en": description}),
            )
        ],
    )


def write_experiment_file(
    path: str,
    description: str,
    display_name: str,
) -> None:
    """
    Write an experiment file.

    Make sure the path corresponds to a path like
    `/experiment_data/description_to_display_name/{expected, unexpected}/<name>`
    (without trailing slash!) The method will append `/model.json`
    for the actual AAS filename.
    """
    # Create the experiment data
    submodel = generate_submodel_with_description_and_display_name(
        description, display_name
    )
    # ensure directory exists
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    # Write the AAS JSON file
    with open(f"{path}/model.json", "w", encoding="utf-8") as file:
        json_serialization.write_aas_json_file(
            file, model.DictObjectStore([submodel]), indent=4
        )


if __name__ == "__main__":
    # Semantic inversion
    write_experiment_file(
        path=f"{BASE_PATH}/expected/semantic_inversion",
        description="Permitted voltage",
        display_name="Allowed voltage",
    )
    #   Similar wording, same meaning
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/semantic_inversion",
        description="Permitted voltage",
        display_name="Maximum voltage",
    )
    #   Similar wording, but “permitted” = normal operating vs
    #   “maximum” = absolute upper safety limit => not the same meaning.

    # Paraphrase / Synonymy
    write_experiment_file(
        path=f"{BASE_PATH}/expected/no_paraphrase_synonymy",
        description="Start time",
        display_name="Beginning time",
    )
    #   Different wording, same meaning
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/paraphrase_synonymy",
        description="Start time",
        display_name="End time",
    )
    #   Different wording, different meaning

    # Partial overlap
    write_experiment_file(
        path=f"{BASE_PATH}/expected/no_partial_overlap",
        description="Material (steel alloy)",
        display_name="Material",
    )
    #   `description` is a more specific instance of the `display_name`
    #   => Correct, but different level of detail
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/partial_overlap",
        description="Surface coating (steel alloy)",
        display_name="Material",
    )
    #   `description` is not just a more detailed version of the `display_name`.

    # Contradiction / factual inconsistency
    write_experiment_file(
        path=f"{BASE_PATH}/expected/no_contradiction",
        description="Suitable for indoor use",
        display_name="For indoor environments",
    )
    #   `description` does not contradict `display_name`
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/contradiction",
        description="Suitable for indoor use",
        display_name="For outdoor environments",
    )
    #   `description` does not contradict `display_name`

    # Ambiguity
    write_experiment_file(
        path=f"{BASE_PATH}/expected/no_ambiguity",
        description="Electrical input power",
        display_name="Power consumption",
    )
    #   No ambiguity
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/ambiguity",
        description="Power",
        display_name="Rated power",
    )
    #   Could be electrical? mechanical? thermal? -> not enough context to know

    # Omission / missing info
    write_experiment_file(
        path=f"{BASE_PATH}/expected/no_omission",
        description="Operating temperature range",
        display_name="Operating temperature",
    )
    #   Semantically still the same
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/omission",
        description="Operating temperature",
        display_name="Temperature",
    )
    #   `display_name` "Temperature" is too vague, could be anything

    # Context-dependent interpretation / words sense disambiguation (WSD)
    write_experiment_file(
        path=f"{BASE_PATH}/expected/context_words_sense_disambiguation",
        description="Mechanical output power",
        display_name="Mechanical power",
    )
    #   Semantically still the same
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/context_words_sense_disambiguation",
        description="Mechanical Power",
        display_name="Power",
    )
    #   `display_name` can only be interpreted in context (could be electrical, thermal, hydraulic)

    # Syntax
    write_experiment_file(
        path=f"{BASE_PATH}/expected/syntax",
        description="Nominal shaft speed",
        display_name="Nominal shaft speed",
    )
    #   No syntax error
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/syntax",
        description="Nominalshaftspeed",
        display_name="Nominal shaft speed",
    )
    #   No spaces in `description`

    # Terminology mismatch
    write_experiment_file(
        path=f"{BASE_PATH}/expected/no_terminology_mismatch",
        description="Shaft diameter",
        display_name="Shaft diameter",
    )
    #   No mismatch
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/terminology_mismatch",
        description="Shaft diameter",
        display_name="Axle length",
    )
    #   Sounds related, but diameter != length

    # Negation mismatch
    write_experiment_file(
        path=f"{BASE_PATH}/expected/no_negation_mismatch",
        description="Suitable for wet environments",
        display_name="Compatible with wet environments",
    )
    #   No mismatch
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/negation_mismatch",
        description="Do not operate in wet conditions",
        display_name="Suitable for wet environments",
    )
    #   `display_name` is negation of `description`

    # Uncommon phrasing / language quality
    write_experiment_file(
        path=f"{BASE_PATH}/expected/no_uncommon_phrasing",
        description="Weight",
        display_name="Weight",
    )
    #   Normal terms used
    write_experiment_file(
        path=f"{BASE_PATH}/unexpected/uncommon_phrasing",
        description="Weight heavy",
        display_name="Heaviness",
    )
    #   Kind of intelligible by a human, but weird
