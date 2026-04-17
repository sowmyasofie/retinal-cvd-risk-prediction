from fastapi import FastAPI, UploadFile, Form
from PIL import Image
import numpy as np
import io

from model_loader import retinal_model
from risk_logic import compute_final_risk

app = FastAPI(title="Retinal CVD Risk Screening API")


def preprocess_image(img: Image.Image):
    img = img.resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)
    return img


@app.get("/")
def root():
    return {"status": "Backend running"}


@app.post("/predict")
async def predict(
    retinal_image: UploadFile,
    age: int = Form(...),
    gender: str = Form(...),
    sys_bp: int | None = Form(None),
    dia_bp: int | None = Form(None),
    diabetes: str = Form(...)
):
    # Load image
    image_bytes = await retinal_image.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    img_tensor = preprocess_image(image)

    # Retinal prediction
    retinal_raw = float(retinal_model.predict(img_tensor)[0][0])
    retinal_score = np.clip((retinal_raw - 0.45) / 0.45, 0, 1)

    # Final risk
    result = compute_final_risk(
        retinal_score=retinal_score,
        age=age,
        sys_bp=sys_bp,
        dia_bp=dia_bp,
        diabetes_status=diabetes
    )

    return result
