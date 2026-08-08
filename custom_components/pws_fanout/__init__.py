"""
PWS Webhook Fanout Integration for Home Assistant.

This integration receives webhook data via Home Assistant's built-in webhook
system and forwards it to multiple configured destinations.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.webhook import async_register, async_unregister

from .const import (
    CONF_DESTINATIONS,
    CONF_METHOD,
    CONF_TIMEOUT,
    CONF_URL,
    CONF_WEBHOOK_ID,
    DEFAULT_METHOD,
    DEFAULT_TIMEOUT,
    DEFAULT_WEBHOOK_ID,
    DOMAIN,
    SUPPORTED_METHODS,
)

_LOGGER = logging.getLogger(__name__)

# Destination schema for validation
DESTINATION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): cv.url,
        vol.Optional(CONF_METHOD, default=DEFAULT_METHOD): vol.In(SUPPORTED_METHODS),
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=60)
        ),
    }
)

# Configuration schema
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_WEBHOOK_ID, default=DEFAULT_WEBHOOK_ID): cv.string,
                vol.Required(CONF_DESTINATIONS): vol.All(
                    cv.ensure_list, [DESTINATION_SCHEMA]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the PWS Fanout integration."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    webhook_id = conf[CONF_WEBHOOK_ID]
    destinations = conf[CONF_DESTINATIONS]

    # Store configuration
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["destinations"] = destinations
    hass.data[DOMAIN]["webhook_id"] = webhook_id

    # Create aiohttp session for forwarding
    session = async_get_clientsession(hass)
    hass.data[DOMAIN]["session"] = session

    # Register the webhook handler
    @callback
    async def handle_webhook(
        hass: HomeAssistant, webhook_id: str, request: Any
    ) -> None:
        """Handle incoming webhook request."""
        _LOGGER.info(
            "Received webhook: method=%s, query_string=%s, content_type=%s",
            request.method,
            request.query_string,
            request.content_type,
        )

        # Get the raw query string exactly as received
        query_string = request.query_string

        # Get content type from original request
        content_type = request.content_type or ""

        # Read raw body exactly as received
        try:
            raw_body = await request.read()
            if raw_body:
                _LOGGER.debug("Raw body size: %d bytes", len(raw_body))
        except Exception as err:
            _LOGGER.error("Error reading request body: %s", err)
            raw_body = b""

        # Forward to all destinations asynchronously
        tasks = [
            forward_to_destination(hass, dest, query_string, raw_body, content_type)
            for dest in destinations
        ]

        # Run all forwarding tasks concurrently
        if tasks:
            asyncio.create_task(_run_forwarding_tasks(tasks))

    async def _run_forwarding_tasks(tasks: list) -> None:
        """Run forwarding tasks and handle results."""
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                _LOGGER.error(
                    "Error forwarding to destination %s: %s",
                    destinations[i][CONF_URL],
                    result,
                )

    # Register webhook
    async_register(hass, DOMAIN, "PWS Fanout Webhook", webhook_id, handle_webhook)

    _LOGGER.info(
        "PWS Fanout integration set up with webhook ID '%s' and %d destinations",
        webhook_id,
        len(destinations),
    )

    return True


async def forward_to_destination(
    hass: HomeAssistant,
    destination: dict[str, Any],
    query_string: str,
    raw_body: bytes,
    original_content_type: str,
) -> None:
    """Forward webhook data to a single destination."""
    url = destination[CONF_URL]
    method = destination[CONF_METHOD]
    timeout = destination[CONF_TIMEOUT]

    session: aiohttp.ClientSession = hass.data[DOMAIN]["session"]

    # Build URL with original query string
    if query_string:
        url = f"{url}?{query_string}"

    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)

        if method == "POST":
            # Forward raw body with original content type
            async with session.post(
                url,
                data=raw_body,
                headers={"Content-Type": original_content_type} if original_content_type else None,
                timeout=timeout_obj,
            ) as response:
                _LOGGER.info(
                    "Forwarded (POST) to %s: status=%s", url, response.status
                )
        else:  # GET
            async with session.get(
                url, timeout=timeout_obj
            ) as response:
                _LOGGER.info(
                    "Forwarded (GET) to %s: status=%s", url, response.status
                )

    except asyncio.TimeoutError:
        _LOGGER.error("Timeout forwarding to %s", url)
        raise
    except aiohttp.ClientError as err:
        _LOGGER.error("Error forwarding to %s: %s", url, err)
        raise


async def async_unload(hass: HomeAssistant, config: ConfigType) -> bool:
    """Unload the PWS Fanout integration."""
    if DOMAIN in hass.data:
        webhook_id = hass.data[DOMAIN].get("webhook_id")
        if webhook_id:
            async_unregister(hass, webhook_id)
            _LOGGER.info("Unregistered webhook '%s'", webhook_id)

        hass.data.pop(DOMAIN, None)

    return True