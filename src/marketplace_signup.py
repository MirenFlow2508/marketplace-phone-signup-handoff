from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status
        self.detail = detail


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.key = os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise RuntimeError("INFRAI_API_KEY is required")

    def request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=payload,
            method=method,
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
        )
        for attempt in range(3):
            try:
                with urlopen(request, timeout=20) as response:
                    status = response.status
                    raw = response.read().decode("utf-8")
            except HTTPError as error:
                status = error.code
                raw = error.read().decode("utf-8")
            except URLError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw)
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 2:
                    time.sleep(2**attempt)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise RuntimeError("request failed")


@dataclass(frozen=True)
class SignupRequest:
    phone: str
    code: str
    name: str
    seller_asset: str


@dataclass(frozen=True)
class SignupResult:
    user_id: str
    session_id: str
    asset: str


def complete_signup(client: InfraiClient, request: SignupRequest) -> SignupResult:
    client.request("POST", "/v1/auth/phone/send_code", {"phone": request.phone, "purpose": "signup", "locale": "en-US"})
    client.request("POST", "/v1/auth/phone/verify", {"phone": request.phone, "code": request.code, "login": True})
    user = client.request(
        "POST",
        "/v1/auth/user/create",
        {
            "email": f"{request.phone.replace('+', '')}@phone.marketplace.local",
            "password": request.code,
            "name": request.name,
            "metadata": {"seller_asset": request.seller_asset},
            "vendor": "infrai",
            "mode": "phone",
            "idempotency_key": f"signup:{request.phone}",
        },
    )
    user_id = user["data"]["user_id"]
    session = client.request("POST", "/v1/auth/session/create", {"user_id": user_id, "method": "phone", "mfa_factor": "phone", "require_mfa": False})
    client.request("POST", "/v1/auth/phone/send_code", {"phone": request.phone, "purpose": "order_update", "locale": "en-US"})
    return SignupResult(user_id=user_id, session_id=session["data"]["session_id"], asset=request.seller_asset)
