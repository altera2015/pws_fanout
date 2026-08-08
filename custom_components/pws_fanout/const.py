"""Constants for the PWS Webhook Fanout integration."""

DOMAIN = "pws_fanout"

# Configuration keys
CONF_WEBHOOK_ID = "webhook_id"
CONF_DESTINATIONS = "destinations"
CONF_URL = "url"
CONF_METHOD = "method"
CONF_TIMEOUT = "timeout"

# Default values
DEFAULT_WEBHOOK_ID = "pws_fanout"
DEFAULT_METHOD = "POST"
DEFAULT_TIMEOUT = 10

# Supported HTTP methods
SUPPORTED_METHODS = ["GET", "POST"]