from src.marketplace_signup import SignupRequest


def test_signup_request_keeps_seller_asset_for_order_handoff():
    request = SignupRequest("+15551234567", "123456", "Mina", "vintage-lamp-42")
    assert request.seller_asset == "vintage-lamp-42"
    assert request.phone.startswith("+")
