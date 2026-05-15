import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


def _read_secret(name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value

    try:
        import streamlit as st

        secret_value = st.secrets.get(name)
        if secret_value:
            return str(secret_value)
    except Exception:
        return None

    return None


def get_supabase_config() -> tuple[str, str]:
    url = _read_secret("SUPABASE_URL")
    key = _read_secret("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
    return url.rstrip("/"), key


def _build_headers(key: str, prefer: str | None = None) -> dict[str, str]:
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def _parse_response(response: requests.Response) -> Any:
    if 200 <= response.status_code < 300:
        if response.text:
            return response.json()
        return None

    try:
        detail = response.json()
    except Exception:
        detail = response.text
    raise RuntimeError(f"Supabase Data API error ({response.status_code}): {detail}")


def rest_get(table: str, params: dict[str, Any], timeout: int = 10) -> list[dict[str, Any]]:
    url, key = get_supabase_config()
    endpoint = f"{url}/rest/v1/{table}"
    response = requests.get(endpoint, headers=_build_headers(key), params=params, timeout=timeout)
    data = _parse_response(response)
    return data or []


def rest_post(table: str, payload: dict[str, Any], timeout: int = 10) -> list[dict[str, Any]]:
    url, key = get_supabase_config()
    endpoint = f"{url}/rest/v1/{table}"
    response = requests.post(
        endpoint,
        headers=_build_headers(key, prefer="return=representation"),
        json=payload,
        timeout=timeout,
    )
    data = _parse_response(response)
    return data or []


def rest_patch(
    table: str,
    payload: dict[str, Any],
    filters: dict[str, Any],
    timeout: int = 10,
) -> list[dict[str, Any]]:
    url, key = get_supabase_config()
    endpoint = f"{url}/rest/v1/{table}"
    response = requests.patch(
        endpoint,
        headers=_build_headers(key, prefer="return=representation"),
        params=filters,
        json=payload,
        timeout=timeout,
    )
    data = _parse_response(response)
    return data or []
