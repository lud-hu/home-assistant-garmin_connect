"""The Garmin Connect integration."""

import asyncio
import logging
from collections.abc import Awaitable
from datetime import date
import datetime
import calendar

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, IntegrationError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DATA_COORDINATOR, DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


def calc_day_ahead_target(
    elevation_gain_current_year: int, target_elevation_gain=100000
) -> int:
    """Calculates the days ahead the yearly elevation gain target. Negative number if behind target."""

    def days_in_year(year=datetime.datetime.now().year):
        return 365 + calendar.isleap(year)

    elevation_gain_per_day = target_elevation_gain / days_in_year()
    target_up_to_today = elevation_gain_per_day * date.today().timetuple().tm_yday
    diff = elevation_gain_current_year - target_up_to_today

    return round(diff / elevation_gain_per_day)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Garmin Connect from a config entry."""

    coordinator = GarminConnectDataUpdateCoordinator(hass, entry=entry)

    if not await coordinator.async_login():
        return False

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {DATA_COORDINATOR: coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class GarminConnectDataUpdateCoordinator(DataUpdateCoordinator):
    """Garmin Connect Data Update Coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Garmin Connect hub."""
        self.entry = entry
        self.hass = hass
        self.in_china = False

        country = self.hass.config.country
        if country == "CN":
            self.in_china = True

        self._api = Garmin(
            entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], self.in_china
        )

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=DEFAULT_UPDATE_INTERVAL
        )

    async def async_login(self) -> bool:
        """Login to Garmin Connect."""
        try:
            await self.hass.async_add_executor_job(self._api.login)
        except (
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ) as err:
            _LOGGER.error("Error occurred during Garmin Connect login request: %s", err)
            return False
        except GarminConnectConnectionError as err:
            _LOGGER.error(
                "Connection error occurred during Garmin Connect login request: %s", err
            )
            raise ConfigEntryNotReady from err
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception(
                "Unknown error occurred during Garmin Connect login request"
            )
            return False

        return True

    async def _async_update_data(self) -> dict:
        """Fetch data from Garmin Connect."""

        summary = {}
        elevation_gain_data = {}
        elevation_gain_current_year = None

        try:
            summary = await self.hass.async_add_executor_job(
                self._api.get_user_summary, date.today().isoformat()
            )
            _LOGGER.debug(f"Summary data: {summary}")

            elevation_gain_data = await self.hass.async_add_executor_job(
                self._api.get_progress_summary_between_dates,
                date.today().replace(month=1, day=1).isoformat(),
                date.today().isoformat(),
                "elevationGain",
                False,
            )
            _LOGGER.debug(f"Elevation Gain data: {elevation_gain_data}")

            elevation_gain_current_year = round(
                elevation_gain_data[0]["stats"]["all"]["elevationGain"]["sum"] / 100
            )
            _LOGGER.debug(f"Elevation Gain value: {elevation_gain_current_year}")

            days_ahead_target = calc_day_ahead_target(
                elevation_gain_current_year,
                100000,
            )
        except KeyError:
            _LOGGER.debug("Elevation Gain data is not available")
        except (
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
            GarminConnectConnectionError,
        ) as error:
            _LOGGER.debug("Trying to relogin to Garmin Connect")
            if not await self.async_login():
                raise UpdateFailed(error) from error
            return {}

        return {
            "lastSyncTimestampGMT": summary["lastSyncTimestampGMT"],
            "totalElevationGainCurrentYear": elevation_gain_current_year,
            "daysAheadElevationTarget": days_ahead_target,
        }
