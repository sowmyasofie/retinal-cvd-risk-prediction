from risk_logic import compute_final_risk

# -------------------------
# TEST CASES
# -------------------------

tests = [
    {
        "name": "Healthy young person",
        "raw_retinal": 0.44,
        "age": 25,
        "sys_bp": 110,
        "dia_bp": 70,
        "diabetes": "no"
    },
    {
        "name": "Middle-aged, high BP",
        "raw_retinal": 0.52,
        "age": 48,
        "sys_bp": 150,
        "dia_bp": 95,
        "diabetes": "no"
    },
    {
        "name": "Diabetic with normal retina",
        "raw_retinal": 0.45,
        "age": 40,
        "sys_bp": 120,
        "dia_bp": 80,
        "diabetes": "yes"
    },
    {
        "name": "Diabetic with abnormal retina",
        "raw_retinal": 0.70,
        "age": 55,
        "sys_bp": 140,
        "dia_bp": 90,
        "diabetes": "yes"
    },
    {
        "name": "Unknown BP, borderline retina",
        "raw_retinal": 0.55,
        "age": 50,
        "sys_bp": None,
        "dia_bp": None,
        "diabetes": "don't know"
    }
]

for t in tests:
    result = compute_final_risk(
        raw_retinal_score=t["raw_retinal"],
        age=t["age"],
        sys_bp=t["sys_bp"],
        dia_bp=t["dia_bp"],
        diabetes_status=t["diabetes"]
    )

    print(f"\nTEST: {t['name']}")
    print("Result:", result)
