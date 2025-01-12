"""Constants for the Garmin Connect integration."""

from datetime import timedelta
from typing import NamedTuple

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfTime

DOMAIN = "garmin_connect_yearly_elevation_gain"
DATA_COORDINATOR = "coordinator"
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)

GARMIN_ENTITY_LIST = {
    "totalElevationGainCurrentYear": [
        "Elevation Gain This Year",
        UnitOfLength.METERS,
        "mdi:elevation-rise",
        SensorDeviceClass.DISTANCE,
        SensorStateClass.MEASUREMENT,
        True,
    ],
    "daysAheadElevationTarget": [
        "Days Ahead/Behind Target",
        UnitOfTime.DAYS,
        "mdi:calendar-today",
        SensorDeviceClass.DURATION,
        SensorStateClass.TOTAL,
        True,
    ],
}


class SERVICE_SETTING(NamedTuple):
    """Options for the service settings, see services.yaml"""

    ONLY_THIS_AS_DEFAULT = "set this as default, unset others"
    DEFAULT = "set as default"
    UNSET_DEFAULT = "unset default"
