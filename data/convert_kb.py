"""
Converts lib/permit-advisory-kb.ts from PermitPredict v8 into correction_comments.json.

Usage:
    python data/convert_kb.py --input /path/to/permit-advisory-kb.ts --output data/correction_comments.json

The script parses the TypeScript file's knowledge snippets and produces structured
JSON that ChromaDB can ingest with proper review_type metadata.
"""
import argparse
import json
import re


REVIEW_TYPE_ALIASES = {
    "eca": "ECA/GeoTech",
    "geotech": "ECA/GeoTech",
    "structural": "Structural",
    "drainage": "Drainage",
    "sepa": "SEPA",
    "land use": "Land Use",
    "landuse": "Land Use",
    "fire": "Fire",
    "mechanical": "Mechanical",
    "electrical": "Electrical",
    "plumbing": "Plumbing",
    "energy": "Energy",
    "planning": "Planning",
}


def extract_knowledge_blocks(ts_source: str) -> list[dict]:
    """
    Extracts knowledge blocks from the TypeScript source.
    Looks for patterns like:  reviewType: "...", content: "..."
    Adjust the regex below once we see the actual file structure.
    """
    records = []
    # Pattern: tries to find objects with reviewType / content fields
    block_pattern = re.compile(
        r'reviewType["\s:]+([^"]+)"[^}]*content["\s:]+([^"]+)"',
        re.IGNORECASE | re.DOTALL,
    )
    for i, match in enumerate(block_pattern.finditer(ts_source)):
        raw_type = match.group(1).strip().lower()
        content = match.group(2).strip()
        review_type = REVIEW_TYPE_ALIASES.get(raw_type, raw_type.title())
        records.append({
            "id": f"{raw_type.replace('/', '_')}_{i:03d}",
            "review_type": review_type,
            "content": content,
            "metadata": {
                "review_type": review_type,
                "applies_to_cost_range": "all",
                "applies_to_permit_types": ["New Building", "Addition/Alteration"],
            },
        })
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to permit-advisory-kb.ts")
    parser.add_argument("--output", default="data/correction_comments.json")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        source = f.read()

    records = extract_knowledge_blocks(source)
    print(f"Extracted {len(records)} records")

    if not records:
        print("WARNING: No records extracted. The TypeScript structure may need a custom parser.")
        print("Please share the file so the regex can be tuned to match its exact format.")
        return

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
