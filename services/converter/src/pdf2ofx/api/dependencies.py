from __future__ import annotations

import hmac
from typing import Annotated

from fastapi import Header, HTTPException, status

from pdf2ofx.settings import get_settings


def require_api_key(
    x_internal_api_key: Annotated[str | None, Header()] = None,
) -> None:
    expected = get_settings().api_key
    provided = x_internal_api_key or ""
    if not hmac.compare_digest(provided.encode(), expected.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave interna inválida.",
        )
