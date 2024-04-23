from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import stripe

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


@patch("stripe.checkout.Session.create")
def test_create_checkout_should_return_url(mock_stripe: Mock, client: "TestClient") -> None:
    mock_stripe.return_value = {"url": "https://example.com/checkout"}
    response = client.post(
        "/payments",
        json={
            "amount": 1000,
            "currency": "USD",
            "payment_method_types": ["card"],
        },
    )

    assert response.status_code == 201
    assert response.json() == {"url": "https://example.com/checkout"}


@patch("stripe.checkout.Session.create")
def test_test_checkout_stripe_error_should_rise_checkout_error(mock_stripe: Mock, client: "TestClient") -> None:
    mock_stripe.side_effect = stripe.StripeError
    response = client.post(
        "/payments",
        json={
            "amount": 1000,
            "currency": "USD",
            "payment_method_types": ["card"],
        },
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "An error occurred while creating the checkout"}
