"""Constants for the experimental P20 live-position integration."""

from datetime import timedelta

DOMAIN = "p20_live_position"
ROBOROCK_DOMAIN = "roborock"
TARGET_MODEL = "roborock.vacuum.a134"
SCAN_INTERVAL = timedelta(seconds=3)

CONF_LEFT_X = "left_x"
CONF_LEFT_Y = "left_y"
CONF_LEFT_OFFSET = "left_offset"
CONF_TOP_X = "top_x"
CONF_TOP_Y = "top_y"
CONF_TOP_OFFSET = "top_offset"

CALIBRATION_KEYS = (
    CONF_LEFT_X,
    CONF_LEFT_Y,
    CONF_LEFT_OFFSET,
    CONF_TOP_X,
    CONF_TOP_Y,
    CONF_TOP_OFFSET,
)
