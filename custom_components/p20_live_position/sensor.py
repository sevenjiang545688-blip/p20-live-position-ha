"""P20 live-position sensor reusing Home Assistant's Roborock session."""

from __future__ import annotations

import logging
from typing import Any

from roborock.roborock_typing import RoborockCommand

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    DOCK_ANCHOR,
    ROBOROCK_DOMAIN,
    SCAN_INTERVAL,
    TARGET_MODEL,
    VACUUM_ENTITY_ID,
)
from .protocol import decode_position, dynamic_data_params

_LOGGER = logging.getLogger(__name__)


def find_p20_coordinator(hass: HomeAssistant):
    """Find the official coordinator that owns the existing P20 connection."""
    for entry in hass.config_entries.async_entries(ROBOROCK_DOMAIN):
        if entry.state is not ConfigEntryState.LOADED or entry.runtime_data is None:
            continue
        for coordinator in entry.runtime_data.values():
            device = getattr(coordinator, "device", None)
            product = getattr(device, "product", None)
            if getattr(product, "model", None) == TARGET_MODEL:
                return coordinator
    raise UpdateFailed("The loaded official Roborock P20 coordinator was not found")


class P20PositionCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll coordinates over the command trait of the existing connection."""

    def __init__(self, hass: HomeAssistant, calibration: dict[str, float]) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="P20 Pro live position",
            update_interval=SCAN_INTERVAL,
        )
        self._roborock_coordinator = None
        self._calibration = calibration

    async def _async_update_data(self) -> dict[str, Any]:
        vacuum_state = self.hass.states.get(VACUUM_ENTITY_ID)
        if vacuum_state is None or vacuum_state.state in {
            "docked",
            "unknown",
            "unavailable",
        }:
            return {
                **DOCK_ANCHOR,
                "updated_at": dt_util.utcnow().isoformat(),
                "connection": "dock_anchor",
            }
        try:
            if self._roborock_coordinator is None:
                self._roborock_coordinator = find_p20_coordinator(self.hass)
            command = self._roborock_coordinator.properties_api.command
            diff = await command.send(RoborockCommand.GET_DYNAMIC_MAP_DIFF)
            if not isinstance(diff, dict):
                raise ValueError("get_dynamic_map_diff returned no object")
            dynamic = await command.send(
                RoborockCommand.GET_DYNAMIC_DATA,
                params=dynamic_data_params(diff),
            )
            if not isinstance(dynamic, dict):
                raise ValueError("get_dynamic_data returned no object")
            return {
                **decode_position(dynamic, self._calibration),
                "updated_at": dt_util.utcnow().isoformat(),
                "connection": (
                    "local"
                    if self._roborock_coordinator.device.is_local_connected
                    else "cloud_fallback"
                ),
            }
        except Exception as error:
            raise UpdateFailed(f"P20 position read failed: {error}") from error


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the live-position sensor."""
    coordinator = P20PositionCoordinator(
        hass, {key: float(value) for key, value in entry.data.items()}
    )
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([P20LivePositionSensor(coordinator)])


class P20LivePositionSensor(
    CoordinatorEntity[P20PositionCoordinator], SensorEntity
):
    """Expose mapped P20 coordinates as one diagnostic entity."""

    _attr_has_entity_name = True
    _attr_name = "实时位置"
    _attr_unique_id = "p20_pro_live_position"
    _attr_icon = "mdi:robot-vacuum"

    @property
    def native_value(self) -> str | None:
        """Return a compact coordinate state."""
        if not self.coordinator.data:
            return None
        return (
            f"{self.coordinator.data['left_percent']},"
            f"{self.coordinator.data['top_percent']}"
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return raw LAN and mapped floorplan coordinates."""
        return dict(self.coordinator.data or {})
