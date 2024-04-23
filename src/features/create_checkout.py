from enum import StrEnum, auto
from functools import cache
from typing import Annotated, Any

import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import AnyUrl, BaseModel

from src.core.dependencies import LoggerDependency, StripeConfigDependency
from src.core.logging import Logger

router = APIRouter()


class PaymentMethod(StrEnum):
    CARD = auto()


class CreateCheckoutRequest(BaseModel):
    amount: int
    currency: str
    payment_method_types: list[PaymentMethod]


class CreateCheckoutResponse(BaseModel):
    url: AnyUrl


class CheckoutService:
    class BaseError(Exception):
        pass

    class CheckoutError(BaseError):
        def __init__(self, message: str | None = None) -> None:
            super().__init__(message or "An error occurred while creating the checkout")

    def __init__(self, stripe_api_key: str, logger: Logger) -> None:
        stripe.api_key = stripe_api_key

        self._log = logger

    def create_checkout(self, data: CreateCheckoutRequest) -> dict[Any, Any]:
        self._log.info("Creating a new checkout session.")
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=data.payment_method_types,  # type: ignore[arg-type]
                line_items=[
                    {
                        "price_data": {
                            "currency": data.currency,
                            "product_data": {
                                "name": "Paymemnt",
                            },
                            "unit_amount": data.amount,
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
            )
        except stripe.StripeError as e:
            self._log.error("An error occurred while creating the checkout.", exc_info=e)
            raise self.CheckoutError from e
        self._log.info("Checkout session created successfully.")
        return session


@cache
def get_stripe_connector(config: StripeConfigDependency, logger: LoggerDependency) -> CheckoutService:
    return CheckoutService(stripe_api_key=config.api_key, logger=logger)


CheckoutServiceDependency = Annotated[CheckoutService, Depends(get_stripe_connector)]


@router.post(
    "/payments",
    response_model=CreateCheckoutResponse,
    summary="Create a new checkout session.",
    status_code=status.HTTP_201_CREATED,
)
def checkout(request: CreateCheckoutRequest, service: CheckoutServiceDependency) -> dict[Any, Any]:
    try:
        return service.create_checkout(request)
    except service.CheckoutError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e
