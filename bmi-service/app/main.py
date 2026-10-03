from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="bmi-service")

ACTIVITY = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}

class Profile(BaseModel):
    weight_kg: float = Field(gt=0)
    height_cm: float = Field(gt=0)
    age: int = Field(gt=0)
    sex: str = Field(pattern="^(male|female)$")
    activity: str = "light"

# Used by Docker's healthcheck to confirm the service is alive
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/bmi")
def bmi(p: Profile):
    value = p.weight_kg / ((p.height_cm / 100) ** 2)
    if value < 18.5: cat = "underweight"
    elif value < 25: cat = "normal"
    elif value < 30: cat = "overweight"
    else: cat = "obese"
    return {"bmi": round(value, 1), "category": cat}

@app.post("/calories")
def calories(p: Profile):
    # Mifflin-St Jeor equation for BMR
    bmr = 10 * p.weight_kg + 6.25 * p.height_cm - 5 * p.age + (5 if p.sex == "male" else -161)
    return {"bmr": round(bmr), "daily_calories": round(bmr * ACTIVITY.get(p.activity, 1.375))}
