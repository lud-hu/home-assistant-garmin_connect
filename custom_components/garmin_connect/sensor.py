"""Platform for Garmin Connect integration."""

from __future__ import annotations

import datetime
import logging
from numbers import Number

import voluptuous as vol
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_ENTITY_ID, CONF_ID, UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from tzlocal import get_localzone

from .const import DATA_COORDINATOR
from .const import DOMAIN as GARMIN_DOMAIN
from .const import GARMIN_ENTITY_LIST

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Garmin Connect sensor based on a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[GARMIN_DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    unique_id = entry.data[CONF_ID]

    entities = []
    for (
        sensor_type,
        (name, unit, icon, device_class, state_class, enabled_by_default),
    ) in GARMIN_ENTITY_LIST.items():

        _LOGGER.debug(
            "Registering entity: %s, %s, %s, %s, %s, %s, %s",
            sensor_type,
            name,
            unit,
            icon,
            device_class,
            state_class,
            enabled_by_default,
        )
        entities.append(
            GarminConnectSensor(
                coordinator,
                unique_id,
                sensor_type,
                name,
                unit,
                icon,
                device_class,
                state_class,
                enabled_by_default,
            )
        )

    async_add_entities(entities)


ENTITY_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): str,
        vol.Required("activity_type"): str,
        vol.Required("setting"): str,
    }
)


class GarminConnectSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Garmin Connect Sensor."""

    def __init__(
        self,
        coordinator,
        unique_id,
        sensor_type,
        name,
        unit,
        icon,
        device_class,
        state_class,
        enabled_default: bool = True,
    ):
        """Initialize a Garmin Connect sensor."""
        super().__init__(coordinator)

        self._unique_id = unique_id
        self._type = sensor_type
        self._device_class = device_class
        self._state_class = state_class
        self._enabled_default = enabled_default

        self._attr_name = name
        self._attr_device_class = self._device_class
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{self._unique_id}_{self._type}"
        self._attr_state_class = state_class

    @property
    def native_value(self):
        """Return the state of the sensor."""

        if not self.coordinator.data or not self.coordinator.data[self._type]:
            return None

        value = self.coordinator.data[self._type]

        return round(value, 2) if isinstance(value, Number) else value

    @property
    def extra_state_attributes(self):
        """Return attributes for sensor."""
        if not self.coordinator.data:
            return {}

        return {
            "last_synced": self.coordinator.data["lastSyncTimestampGMT"],
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return {
            "identifiers": {(GARMIN_DOMAIN, self._unique_id)},
            "name": "Garmin Connect Yearly Elevation Gain",
            "manufacturer": "Garmin Connect",
        }

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self._enabled_default

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self.coordinator.data
            and self._type in self.coordinator.data
        )
