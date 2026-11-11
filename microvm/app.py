import uuid
import uvicorn
from fastapi import FastAPI, status
import pydantic
import decimal


# Application instance
app = FastAPI(title="Movements API")


# Models
class Movement(pydantic.BaseModel):
    id: str = pydantic.Field(default=str(uuid.uuid4()))
    description: str
    amount: decimal.Decimal
    type: str


fake_movements_db: list[Movement] = [
    Movement(
        description="Salario mensual",
        amount=decimal.Decimal(value=2500.00),
        type="income"
    )
]


# Endpoints
@app.get("/", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy"}


@app.get("/movements", response_model=list[Movement], status_code=status.HTTP_200_OK)
def get_movements():
    return fake_movements_db


@app.post("/movements", response_model=Movement, status_code=status.HTTP_201_CREATED)
def create_movement(movement_in: Movement):
    new_movement = Movement(
        description=movement_in.description,
        amount=movement_in.amount,
        type=movement_in.type,
    )
    fake_movements_db.append(new_movement)
    return new_movement


# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
