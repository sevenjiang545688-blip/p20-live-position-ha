"""Experimental P20 live position using the official Roborock connection."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from urllib.request import urlopen

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

PLATFORMS = ["sensor"]

_LOGGER = logging.getLogger(__name__)
_ASSET_URL = "http://10.0.2.2:8767/micro-home-zoom-card.js"
_ASSET_SHA256 = "c6cd35744f28b8cb0a3d90a11a4d4c57f29d39f54aa7e604884b8b18ec1fe770"


def _migrate_micro_home_asset(destination: Path) -> None:
    """Copy the verified dashboard module into /config/www once."""
    if destination.is_file():
        current = hashlib.sha256(destination.read_bytes()).hexdigest()
        if current == _ASSET_SHA256:
            return

    with urlopen(_ASSET_URL, timeout=15) as response:
        payload = response.read()

    actual = hashlib.sha256(payload).hexdigest()
    if actual != _ASSET_SHA256:
        raise ValueError(f"Unexpected micro-home asset SHA-256: {actual}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".js.tmp")
    temporary.write_bytes(payload)
    temporary.replace(destination)
    _LOGGER.info("Migrated micro-home dashboard module to %s", destination)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    destination = Path(hass.config.path("www", "micro-home-zoom-card.js"))
    try:
        await hass.async_add_executor_job(_migrate_micro_home_asset, destination)
    except Exception:  # noqa: BLE001 - migration must never block the sensor
        _LOGGER.exception("Could not migrate the micro-home dashboard module")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
