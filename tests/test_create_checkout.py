from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import stripe
from fastapi import status

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

URL = "/api/payments/checkout"


@patch("stripe.checkout.Session.create")
def test_create_checkout(mock_stripe: Mock, client: TestClient) -> None:
    mock_stripe.return_value = {"url": "https://example.com/checkout"}
    response = client.post(
        URL,
        json={
            "amount": 1000,
            "currency": "USD",
            "payment_method_types": ["card"],
        },
    )

    assert response.status_code == status.HTTP_202_ACCEPTED


@patch("stripe.checkout.Session.create")
def test_create_checkout_raises_checkout_error(mock_stripe: Mock, client: TestClient) -> None:
    mock_stripe.side_effect = stripe.StripeError
    response = client.post(
        URL,
        json={
            "amount": 1000,
            "currency": "USD",
            "payment_method_types": ["card"],
        },
    )

    assert response.status_code == 503
