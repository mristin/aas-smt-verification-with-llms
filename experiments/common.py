"""Provide shared functionality across the experiments."""

JSONSCHEMA = """\
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Improvement Suggestion",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["path", "explanation", "suggestion"],
    "properties": {
      "path": {
        "type": "string",
        "description": "ID-short path to the offending element",
        "examples": [
          "https://example.com/something",
          "urn:example.com:something"
        ]
      },
      "explanation": {
        "type": "string",
        "description": "Explanation of the semantic mismatch",
        "examples": [
          "Semantic mismatch between the concept description and unit. Length should be given in meters, while J (Joule) was indicated."
        ]
      },
      "suggestion": {
        "type": "string",
        "description": "How the semantic mismatch can be fixed",
        "examples": ["m"]
      }
    },
    "additionalProperties": false
  }
}
"""
