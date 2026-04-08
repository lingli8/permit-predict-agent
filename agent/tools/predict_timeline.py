import os
import requests
from langchain_core.tools import tool

PERMITPREDICT_API_URL = os.getenv("PERMITPREDICT_API_URL", "https://permitpredict.vercel.app")


@tool
def predict_timeline(
    permit_type: str,
    permit_class: str,
    estimated_cost: float,
) -> str:
    """Predict the permit processing timeline using the ML model.
    Use this when the user asks how long a permit will take to be approved.

    Args:
        permit_type: e.g. 'New Building', 'Addition/Alteration', 'Demolition'
        permit_class: e.g. 'Single Family/Duplex', 'Multifamily', 'Commercial'
        estimated_cost: project cost in dollars
    """
    try:
        response = requests.post(
            f"{PERMITPREDICT_API_URL}/api/predict",
            json={
                "permitType": permit_type,
                "permitClass": permit_class,
                "estProjectCost": str(estimated_cost),
            },
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        days = result.get("predictedDays") or result.get("prediction")
        confidence = result.get("confidence", "")
        factors = result.get("factors", [])
        msg = f"Predicted processing time: {days} days"
        if confidence:
            msg += f" (confidence: {confidence})"
        if factors:
            top = factors[:2]
            msg += "\nKey factors: " + "; ".join(f.get("description", "") for f in top if f.get("description"))
        return msg
    except requests.HTTPError as e:
        return f"Timeline prediction unavailable (HTTP {e.response.status_code}). Contact SDCI at (206) 684-8850 for estimates."
    except requests.RequestException as e:
        return f"Timeline prediction unavailable: {str(e)}"
