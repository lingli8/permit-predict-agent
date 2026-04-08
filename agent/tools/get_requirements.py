from langchain_core.tools import tool

# Sourced from permit-advisory-kb.ts — preserves v8 rule-based logic
REVIEW_KB: dict = {
    "ECA/GeoTech": {
        "name": "ECA / Geotechnical Review",
        "description": "Environmentally Critical Areas review including geotechnical assessment for landslide, liquefaction, peat settlement, and steep slope hazards.",
        "avg_days_added": 45,
        "requirements": [
            "Geotechnical report signed by WA-licensed geotechnical engineer",
            "Slope stability analysis (required for lots with >15% grade)",
            "ECA boundary delineation based on current LiDAR data (licensed geologist)",
            "Seismic hazard evaluation per ASCE 7",
            "Drainage plan compatible with ECA buffer requirements",
        ],
    },
    "Drainage": {
        "name": "Drainage / Stormwater Review",
        "description": "Stormwater management review for compliance with Seattle Stormwater Code and SPU requirements.",
        "avg_days_added": 30,
        "requirements": [
            "Stormwater drainage report using current WWHM model version",
            "Side sewer plan with SPU connection permit reference",
            "Infiltration testing results (per SPU methods) if using infiltration",
            "Stormwater site plan showing all impervious surfaces",
            "Recorded maintenance agreement for private stormwater facilities",
        ],
    },
    "Structural": {
        "name": "Structural Review",
        "description": "Structural engineering review for code compliance with IBC/IRC and Seattle amendments.",
        "avg_days_added": 35,
        "requirements": [
            "Structural calculations signed and stamped by WA-licensed PE",
            "Complete lateral load path diagram (roof to foundation)",
            "Hold-down and anchor bolt schedule",
            "Foundation design matching geotechnical recommendations",
            "Connection details per AISC or NDS (no generic notes)",
            "Seismic detailing per Risk Category (special inspection schedule if RC-II+)",
        ],
    },
    "Zoning": {
        "name": "Zoning / Land Use Review",
        "description": "Review for compliance with Seattle Municipal Code Title 23 (Land Use Code) including FAR, height, setbacks, and lot coverage.",
        "avg_days_added": 25,
        "requirements": [
            "FAR calculation per SMC 23.86.006 (with exempt area tabulation)",
            "Site plan with all setbacks dimensioned",
            "Lot coverage calculation including all structures and ADU",
            "Height diagram showing measurement datum",
            "Parking count and stall dimensions per SMC 23.54",
        ],
    },
    "Energy": {
        "name": "Energy Code Review",
        "description": "Review for compliance with Washington State Energy Code (WSEC) residential or commercial sections.",
        "avg_days_added": 20,
        "requirements": [
            "WSEC compliance form (residential checklist or COMcheck report)",
            "UA calculation including all envelope components",
            "Mechanical equipment cut sheets showing rated efficiency",
            "Duct leakage testing protocol specification",
            "Room-by-room lighting power density (LPD) calculation",
        ],
    },
    "Fire": {
        "name": "Fire / Life Safety Review",
        "description": "Seattle Fire Department review for fire access, sprinkler requirements, and life safety compliance.",
        "avg_days_added": 25,
        "requirements": [
            "Site plan showing fire access road (min 20 ft wide) and turning radius",
            "Fire hydrant locations with dimensions to structure",
            "Fire sprinkler system layout (if required by occupancy/area)",
            "Egress plan with travel distances and exit locations",
            "Fire-resistance-rated assembly details with UL/GA listing numbers",
        ],
    },
    "Mechanical": {
        "name": "Mechanical Review",
        "description": "Review of HVAC, plumbing, and mechanical systems for code compliance.",
        "avg_days_added": 15,
        "requirements": [
            "Mechanical ventilation calculations per ASHRAE 62.1 / IMC (commercial)",
            "Gas piping sizing table for total BTU load",
            "Type I/II hood details with capture velocity and makeup air calcs (restaurants)",
            "Heat pump manufacturer dB(A) ratings and noise ordinance compliance",
            "Refrigerant piping routing, insulation, and leak detection details",
        ],
    },
}

PERMIT_REQUIREMENTS: dict[str, list[str]] = {
    "New Building": [
        "Site plan (to scale, showing all setbacks and impervious surfaces)",
        "Architectural drawings (floor plans, elevations, sections)",
        "Structural drawings with PE stamp",
        "Energy code compliance form (WSEC checklist or COMcheck)",
        "Mechanical, electrical, and plumbing plans",
        "Geotechnical report (if in ECA or on steep slope)",
        "Stormwater management plan",
        "SEPA environmental checklist (if over threshold)",
    ],
    "Addition/Alteration": [
        "Existing conditions survey showing current structure",
        "Proposed addition/alteration plans",
        "Structural calculations (if structural work is involved)",
        "Energy code compliance for altered areas",
        "Updated site plan showing proposed changes",
    ],
    "Demolition": [
        "Demolition plan showing scope of work",
        "Hazardous materials (asbestos/lead) survey report",
        "Utilities disconnection confirmation from all utilities",
        "Erosion control plan (if excavation involved)",
    ],
    "Grading": [
        "Grading and drainage plan (licensed civil engineer)",
        "Erosion and sediment control plan",
        "Geotechnical report (if slopes >15% or in ECA)",
        "Stormwater pollution prevention plan (SWPPP)",
    ],
}


def _match_permit_type(permit_type: str) -> str:
    """Fuzzy match user input to a canonical permit type key."""
    pt = permit_type.lower()
    if any(w in pt for w in ("new", "construct", "build")):
        return "New Building"
    if any(w in pt for w in ("addition", "alteration", "renovation", "remodel", "expand")):
        return "Addition/Alteration"
    if any(w in pt for w in ("demo", "tear")):
        return "Demolition"
    if any(w in pt for w in ("grade", "grading", "excavat")):
        return "Grading"
    return permit_type  # exact match fallback


@tool
def get_requirements(permit_type: str, permit_class: str = "") -> str:
    """Get the standard permit requirements and likely review types for a specific permit.
    Use this when the user asks what they need to apply for a permit, or what reviews will be triggered."""
    canonical = _match_permit_type(permit_type)
    reqs = PERMIT_REQUIREMENTS.get(canonical, PERMIT_REQUIREMENTS.get(permit_type, ["Contact SDCI for specific requirements: (206) 684-8850"]))
    header = f"Requirements for {canonical}"
    if permit_class:
        header += f" ({permit_class})"

    lines = [header + ":", ""]
    lines += [f"  • {r}" for r in reqs]

    # Identify likely review types based on permit type
    likely_reviews = []
    if canonical in ("New Building", "Addition/Alteration"):
        likely_reviews = ["Zoning", "Structural", "Energy"]
        if canonical == "New Building":
            likely_reviews += ["Fire", "Drainage"]
    if permit_class and any(w in permit_class.lower() for w in ("commercial", "institutional", "mixed")):
        likely_reviews.append("Mechanical")

    if likely_reviews:
        lines += ["", "Likely review types (with avg days added):"]
        for rt in dict.fromkeys(likely_reviews):  # deduplicate, preserve order
            info = REVIEW_KB.get(rt, {})
            days = info.get("avg_days_added", "?")
            lines.append(f"  • {rt}: +{days} days avg")

    return "\n".join(lines)
