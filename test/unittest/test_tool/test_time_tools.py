"""Unit tests for oxygent.preset_tools.time_tools."""

import re

import pytest

from oxygent.preset_tools.time_tools import convert_time, get_current_time


# ──────────────────────────────────────────────────────────────────────────────
# get_current_time
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_current_time_default():
    result = await get_current_time(timezone=None)
    assert "CST" in result or "Asia" in result or re.search(r"\d{4}-\d{2}-\d{2}", result)


@pytest.mark.asyncio
async def test_get_current_time_utc():
    result = await get_current_time(timezone="UTC")
    assert "UTC" in result


@pytest.mark.asyncio
async def test_get_current_time_new_york():
    result = await get_current_time(timezone="America/New_York")
    assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", result)


@pytest.mark.asyncio
async def test_get_current_time_format():
    result = await get_current_time(timezone="Europe/London")
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \w+", result)


# ──────────────────────────────────────────────────────────────────────────────
# convert_time
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_convert_time_basic():
    result = await convert_time(
        source_timezone="UTC",
        time="12:00",
        target_timezone="Asia/Shanghai",
    )
    # UTC 12:00 -> CST ~20:00 (exact offset depends on pytz LMT handling)
    assert result.startswith("20:")


@pytest.mark.asyncio
async def test_convert_time_same_timezone():
    result = await convert_time(
        source_timezone="UTC",
        time="15:30",
        target_timezone="UTC",
    )
    assert result == "15:30"


@pytest.mark.asyncio
async def test_convert_time_none_defaults():
    result = await convert_time(
        source_timezone=None,
        time=None,
        target_timezone=None,
    )
    assert result == "00:00"


@pytest.mark.asyncio
async def test_convert_time_format():
    result = await convert_time(
        source_timezone="America/New_York",
        time="08:00",
        target_timezone="Europe/London",
    )
    assert re.match(r"\d{2}:\d{2}", result)
