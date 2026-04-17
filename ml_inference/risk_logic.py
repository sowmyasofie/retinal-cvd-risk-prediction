import numpy as np


# ---------------------------
# Risk Components
# ---------------------------

def age_risk(age: int) -> float:
    if age < 30:
        return 0.1
    elif age < 45:
        return 0.3
    elif age < 60:
        return 0.55
    else:
        return 0.75


def bp_risk(sys_bp: int | None, dia_bp: int | None) -> float:
    if sys_bp is None or dia_bp is None:
        return 0.3

    if sys_bp < 120 and dia_bp < 80:
        return 0.1
    elif sys_bp < 140 or dia_bp < 90:
        return 0.45
    else:
        return 0.75


def diabetes_risk(status: str) -> float:
    status = status.lower()

    if status == "yes":
        return 1.0
    elif status == "no":
        return 0.2
    else:
        return 0.5


# ---------------------------
# Clinical Index
# ---------------------------

def clinical_index(age, sys_bp, dia_bp, diabetes_status):
    return np.clip(
        0.4 * age_risk(age) +
        0.35 * bp_risk(sys_bp, dia_bp) +
        0.25 * diabetes_risk(diabetes_status),
        0,
        1
    )


# ---------------------------
# Explanation (Detailed)
# ---------------------------

def generate_explanation(category, age, sys_bp, dia_bp, diabetes_status):

    base_text = f"""
This cardiovascular risk estimation is derived from retinal microvascular
analysis combined with structured clinical parameters.

Patient Profile:
• Age: {age} years
• Blood Pressure: {sys_bp}/{dia_bp} mmHg
• Diabetes Status: {diabetes_status}
"""

    if category == "Low Risk":
        base_text += """
Current findings indicate stable cardiovascular condition with no major
high-risk indicators detected. Preventive lifestyle maintenance is advised
to sustain long-term vascular health.
"""

    elif category == "Moderate Risk":
        base_text += """
There are moderate cardiovascular risk indicators present.
These findings suggest early vascular stress. Timely lifestyle
modification and clinical monitoring can significantly reduce
future cardiovascular events.
"""

    else:
        base_text += """
The combined retinal and clinical indicators suggest elevated
cardiovascular risk. Immediate clinical evaluation and risk
factor control are strongly recommended to prevent potential
cardiac or cerebrovascular complications.
"""

    return base_text.strip()


# ---------------------------
# Recommendations (Half Page Style)
# ---------------------------

def generate_recommendations(category, sys_bp, dia_bp, diabetes_status):

    recommendations = []

    if category == "Low Risk":
        recommendations.extend([
            "Maintain balanced diet rich in vegetables, fruits and whole grains.",
            "Engage in at least 150 minutes of moderate exercise weekly.",
            "Monitor blood pressure annually.",
            "Maintain healthy BMI and waist circumference.",
            "Avoid smoking and excessive alcohol intake.",
            "Continue periodic health screening."
        ])

    elif category == "Moderate Risk":
        recommendations.extend([
            "Reduce dietary sodium intake (DASH-style diet recommended).",
            "Increase cardiovascular exercise frequency.",
            "Monitor blood pressure monthly.",
            "Perform lipid profile screening.",
            "Weight management through structured diet plan.",
            "Consult physician for preventive cardiovascular assessment.",
            "Manage stress using relaxation techniques."
        ])

    else:  # High Risk
        recommendations.extend([
            "Immediate consultation with cardiologist or physician.",
            "Comprehensive cardiac screening (ECG, Echo, lipid profile).",
            "Strict blood pressure control (<130/80 mmHg recommended).",
            "Strict glycemic control under medical supervision.",
            "Adopt heart-protective Mediterranean-style diet.",
            "Avoid smoking completely.",
            "Structured medical follow-up every 3–6 months.",
            "Monitor for symptoms such as chest pain or breathlessness."
        ])

    return recommendations


# ---------------------------
# Final Fusion Logic
# ---------------------------

def compute_final_risk(
    retinal_score: float,
    age: int,
    sys_bp: int | None,
    dia_bp: int | None,
    diabetes_status: str
) -> dict:

    clin = clinical_index(age, sys_bp, dia_bp, diabetes_status)

    # Balanced fusion
    risk = 0.55 * retinal_score + 0.45 * clin

    # Strong clinical corrections
    if diabetes_status.lower() == "yes":
        risk = max(risk, 0.60)

    if sys_bp and dia_bp:
        if sys_bp >= 140 or dia_bp >= 90:
            risk = max(risk, 0.55)

    risk = np.clip(risk, 0, 1)

    # Categories
    if risk < 0.35:
        category = "Low Risk"
    elif risk < 0.65:
        category = "Moderate Risk"
    else:
        category = "High Risk"

    return {
        "risk_category": category,
        "risk_percentage": round(risk * 100, 2),
        "explanation": generate_explanation(category, age, sys_bp, dia_bp, diabetes_status),
        "recommendations": generate_recommendations(category, sys_bp, dia_bp, diabetes_status)
    }
