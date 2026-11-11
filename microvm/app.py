from typing import List, Optional
from uuid import uuid4
import uvicorn
from fastapi import FastAPI, status
from pydantic import BaseModel, Field

# Application instance
app = FastAPI(title="Fake Movements API")


# Models
class MovementCreate(BaseModel):
    description: str = Field(..., example="Pago de servicios")
    amount: float = Field(..., gt=0, example=150.50)
    type: str = Field(..., pattern="^(income|expense)$", example="expense")


class Movement(MovementCreate):
    id: str


fake_movements_db: List[Movement] = [
    Movement(id=str(uuid4()), description="Salario mensual", amount=2500.00, type="income")
]


# Endpoints
@app.get("/", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy", "service": "movements-api"}


@app.get("/movements", response_model=List[Movement], status_code=status.HTTP_200_OK)
def get_movements():
    return fake_movements_db


@app.post("/movements", response_model=Movement, status_code=status.HTTP_201_CREATED)
def create_movement(movement_in: MovementCreate):
    new_movement = Movement(
        id=str(uuid4()),
        description=movement_in.description,
        amount=movement_in.amount,
        type=movement_in.type,
    )
    fake_movements_db.append(new_movement)
    return new_movement


# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
