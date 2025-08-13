
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from schemas.rates_schema import RateResponseSchema, RateSchema

router = APIRouter(prefix="/rates", tags=["Rates"])

@router.get("", status_code=status.HTTP_200_OK, response_model=RateResponseSchema)
async def rates(base: str = 'USD', db: Session = Depends(get_db)):
    # TODO: Implement the logic to fetch or calculate the rates based on the provided rate schema.
    if base == "USD":
        # Example logic for USD base rate
        rates = {
            "COP": 4134.71,
        }
    elif base == "COP":
        # Example logic for COP base rate
        rates = {
            "USD": 0.00024
        }
    rate_response = RateResponseSchema(
        base=base,
        rates=rates
    )
    return rate_response
