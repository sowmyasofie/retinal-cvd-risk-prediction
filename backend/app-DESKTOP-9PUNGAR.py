from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from tensorflow.keras.preprocessing import image
from model_loader import retinal_model
import sys
import os

# Allow importing risk_logic from ml_inference
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml_inference"))
from risk_logic import compute_final_risk

app = FastAPI(title="Retinal CVD Risk API")

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------
# Image preprocessing
# ------------------------------------------

def preprocess_image(uploaded_file):
    img = image.load_img(uploaded_file, target_size=(224, 224))
    img = image.img_to_array(img) / 255.0
    return np.expand_dims(img, axis=0)


# ------------------------------------------
# Main Prediction Endpoint
# ------------------------------------------

@app.post("/predict")
async def predict_risk(
    file: UploadFile = File(...),
    age: int = Form(...),
    sex: str = Form(...),
    sys_bp: int = Form(None),
    dia_bp: int = Form(None),
    diabetes: str = Form(...)
):

    # Save uploaded image temporarily
    temp_path = "temp_image.jpg"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Preprocess
    img_tensor = preprocess_image(temp_path)

    # CNN Prediction
    raw_retinal_score = float(
        retinal_model.predict(img_tensor)[0][0]
    )

    # Calibrate raw retinal output (screening normalization)
    calibrated_retinal_score = float(
    	np.clip((raw_retinal_score - 0.45) / 0.45, 0, 1)
    )

    # Risk Logic
    result = compute_final_risk(
        retinal_score=calibrated_retinal_score,
        age=age,
        sys_bp=sys_bp,
        dia_bp=dia_bp,
        diabetes_status=diabetes
    )

    # Remove temp file
    os.remove(temp_path)

    return result

#---------------------
# PDF
#---------------------

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from fastapi.responses import FileResponse
import os


from pydantic import BaseModel
from typing import List


class ReportRequest(BaseModel):
    age: int
    sex: str
    sys_bp: int | None = None
    dia_bp: int | None = None
    diabetes: str
    risk_percentage: float
    risk_category: str
    explanation: str
    recommendations: List[str]


@app.post("/download-report")
async def download_report(data: ReportRequest):


    file_path = "Retinal_CVD_Risk_Report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # ===============================
    # TITLE
    # ===============================
    elements.append(Paragraph(
        "Retinal Cardiovascular Risk Assessment Report",
        styles["Heading1"]
    ))
    elements.append(Spacer(1, 0.3 * inch))

    # ===============================
    # PATIENT DETAILS TABLE
    # ===============================
    patient_info = [
    	["Age", str(data.age)],
    	["Sex", data.sex],
    	["Systolic BP (mmHg)", str(data.sys_bp) if data.sys_bp else "Not Provided"],
    	["Diastolic BP (mmHg)", str(data.dia_bp) if data.dia_bp else "Not Provided"],
    	["Diabetes Status", data.diabetes]
    ]

    table = Table(patient_info, colWidths=[2.5 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(Paragraph("Patient Clinical Details", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # ===============================
    # RISK RESULT
    # ===============================
    elements.append(Paragraph("Risk Assessment Result", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        f"Predicted Risk Percentage: {data.risk_percentage}%",
        styles["Normal"]
    ))

    elements.append(Paragraph(
        f"Risk Category: {data.risk_category}",
        styles["Normal"]
    ))

    elements.append(Spacer(1, 0.4 * inch))

    # ===============================
    # INTERPRETATION
    # ===============================
    elements.append(Paragraph("Clinical Interpretation", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        data.explanation,
        styles["Normal"]
    ))

    elements.append(Spacer(1, 0.4 * inch))

    # ===============================
    # DYNAMIC RECOMMENDATIONS
    # ===============================
    elements.append(Paragraph(
        "Recommended Precautions & Lifestyle Guidance",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 0.2 * inch))

    recommendations = data.recommendations

    if recommendations:
        bullet_points = [
            ListItem(Paragraph(rec, styles["Normal"]))
            for rec in recommendations
        ]

        elements.append(
            ListFlowable(
                bullet_points,
                bulletType="bullet"
            )
        )

    elements.append(Spacer(1, 0.5 * inch))

    # ===============================
    # DISCLAIMER
    # ===============================
    elements.append(Paragraph("Disclaimer", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "This AI-based screening tool is intended for educational and early risk identification purposes only. "
        "It does not replace professional medical diagnosis or treatment. "
        "Please consult a qualified healthcare provider for comprehensive evaluation and clinical decisions.",
        styles["Italic"]
    ))

    # Build PDF
    doc.build(elements)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="Retinal_CVD_Risk_Report.pdf"
    )

