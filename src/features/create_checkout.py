from decimal import Decimal
from enum import StrEnum, auto
from functools import cache
from typing import Annotated, Any
from uuid import UUID, uuid4

import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import AnyUrl, BaseModel, Field
from pydantic_extra_types.currency_code import Currency

from src.core.config import StripeConfig
from src.core.dependencies import LoggerDependency, StripeConfigDependency
from src.core.logging import Logger

router = APIRouter()


class PaymentMethod(StrEnum):
    CARD = auto()


class CreateCheckoutRequest(BaseModel):
    amount: Annotated[Decimal, Field(..., ge=0)]
    currency: Currency
    payment_method_types: list[PaymentMethod]


class CreateCheckoutResponse(BaseModel):
    url: AnyUrl


class CheckoutService:
    class BaseError(Exception):
        pass

    class CheckoutError(BaseError):
        def __init__(self, message: str | None = None) -> None:
            super().__init__(message or "An error occurred while creating the checkout")

    def __init__(self, logger: Logger, config: StripeConfig) -> None:
        stripe.api_key = config.api_key

        self._log = logger
        self._config = config

    def create_checkout(self, data: CreateCheckoutRequest) -> dict[Any, Any]:
        session_id = uuid4()
        self._log.info("Creating a new checkout session.", session_id=session_id)
        request_data = self._map_data(data, session_id=session_id)
        try:
            session = stripe.checkout.Session.create(**request_data)
        except stripe.StripeError as e:
            self._log.error(
                "An error occurred while creating the checkout.",
                exc_info=e,
                session_id=session_id,
            )
            raise self.CheckoutError from e
        self._log.info("Checkout session created successfully.", session_id=session_id)
        return session

    def _map_data(self, data: CreateCheckoutRequest, session_id: UUID) -> dict[str, Any]:
        return {
            "payment_method_types": data.payment_method_types,
            "line_items": [
                {
                    "price_data": {
                        "currency": data.currency,
                        "product_data": {"name": "Paymemnt"},
                        "unit_amount": int(data.amount.quantize(Decimal("1.00")) * 100),
                    },
                    "quantity": 1,
                },
            ],
            "metadata": {"session_id": str(session_id)},
            "mode": "payment",
            "success_url": self._config.success_url,
        }


@cache
def get_stripe_connector(config: StripeConfigDependency, logger: LoggerDependency) -> CheckoutService:
    return CheckoutService(logger=logger, config=config)


CheckoutServiceDependency = Annotated[CheckoutService, Depends(get_stripe_connector)]


@router.post(
    "/checkout",
    response_model=CreateCheckoutResponse,
    summary="Create a new checkout session.",
    status_code=status.HTTP_202_ACCEPTED,
)
def checkout(request: CreateCheckoutRequest, service: CheckoutServiceDependency) -> dict[Any, Any]:
    try:
        return service.create_checkout(request)
    except service.CheckoutError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e
