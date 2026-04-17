import numpy as np

# ---------------------------
# Individual risk components
# ---------------------------

def age_risk(age: int) -> float:
    if age < 30:
        return 0.1
    elif age < 45:
        return 0.25
    elif age < 60:
        return 0.5
    else:
        return 0.75


def bp_risk(sys_bp: int | None, dia_bp: int | None) -> float:
    if sys_bp is None or dia_bp is None:
        return 0.3  # unknown BP → neutral

    if sys_bp < 120 and dia_bp < 80:
        return 0.1
    elif sys_bp < 140 or dia_bp < 90:
        return 0.4
    else:
        return 0.7


def diabetes_risk(status: str) -> float:
    status = status.lower()

    if status == "yes":
        return 1.0   # VERY IMPORTANT
    elif status == "no":
        return 0.2
    else:  # "don't know"
        return 0.5


# ---------------------------
# Clinical risk index
# ---------------------------

def clinical_index(
    age: int,
    sys_bp: int | None,
    dia_bp: int | None,
    diabetes_status: str
) -> float:
    return np.clip(
        0.4 * age_risk(age) +
        0.35 * bp_risk(sys_bp, dia_bp) +
        0.25 * diabetes_risk(diabetes_status),
        0,
        1
    )


# ---------------------------
# Final fusion logic
# ---------------------------

def compute_final_risk(
    retinal_score: float,
    age: int,
    sys_bp: int | None,
    dia_bp: int | None,
    diabetes_status: str
) -> dict:
    """
    retinal_score: calibrated value between 0 and 1
    """

    clin = clinical_index(age, sys_bp, dia_bp, diabetes_status)

    # Hard rule: diabetes + retinal signal → cannot be low risk
    if diabetes_status.lower() == "yes" and retinal_score > 0.3:
        final_score = max(retinal_score, 0.7)
    else:
        final_score = 0.65 * retinal_score + 0.35 * clin

    # Risk categories (NO probabilities shown)
    if final_score < 0.35:
        category = "Low Risk"
    elif final_score < 0.65:
        category = "Moderate Risk"
    else:
        category = "High Risk"

    return {
        "risk_category": category
    }
