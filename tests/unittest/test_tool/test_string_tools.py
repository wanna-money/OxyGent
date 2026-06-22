"""Unit tests for oxygent.preset_tools.string_tools."""

import json

import pytest

from oxygent.preset_tools.string_tools import (
    extract_emails,
    extract_urls,
    validate_email,
)


# ──────────────────────────────────────────────────────────────────────────────
# extract_emails
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_extract_emails_basic():
    text = "Contact us at alice@example.com or bob@test.org for details."
    result = json.loads(await extract_emails(text=text))
    assert set(result) == {"alice@example.com", "bob@test.org"}


@pytest.mark.asyncio
async def test_extract_emails_dedup():
    text = "alice@ex.com and alice@ex.com again"
    result = json.loads(await extract_emails(text=text))
    assert result == ["alice@ex.com"]


@pytest.mark.asyncio
async def test_extract_emails_empty():
    result = json.loads(await extract_emails(text="no emails here"))
    assert result == []


@pytest.mark.asyncio
async def test_extract_emails_complex():
    text = "user.name+tag@domain.co.uk is valid"
    result = json.loads(await extract_emails(text=text))
    assert len(result) == 1
    assert "user.name+tag@domain.co.uk" in result


# ──────────────────────────────────────────────────────────────────────────────
# extract_urls
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_extract_urls_http_and_https():
    text = "Visit http://example.com or https://secure.example.com"
    result = json.loads(await extract_urls(text=text))
    assert len(result) == 2


@pytest.mark.asyncio
async def test_extract_urls_empty():
    result = json.loads(await extract_urls(text="no urls here"))
    assert result == []


# ──────────────────────────────────────────────────────────────────────────────
# validate_email
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_validate_email_valid():
    result = json.loads(await validate_email(email="user@example.com"))
    assert result["is_valid"] is True
    assert result["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_validate_email_invalid():
    result = json.loads(await validate_email(email="invalid.email@"))
    assert result["is_valid"] is False


@pytest.mark.asyncio
async def test_validate_email_no_tld():
    result = json.loads(await validate_email(email="missing@domain"))
    assert result["is_valid"] is False


@pytest.mark.asyncio
async def test_validate_email_with_plus():
    result = json.loads(await validate_email(email="user+tag@domain.com"))
    assert result["is_valid"] is True
