# PWS Webhook Fanout - Home Assistant Integration

This Home Assistant integration receives webhook data via Home Assistant's built-in webhook system and forwards it to multiple configured destinations. It replaces the standalone `server.py` with a proper Home Assistant integration.

## Features

- Uses Home Assistant's built-in webhook system (no separate server needed)
- Asynchronous forwarding using `aiohttp` (no threading required)
- YAML-based configuration
- Support for multiple destinations
- Configurable HTTP method (GET/POST) per destination
- Configurable timeout per destination
- Concurrent forwarding to all destinations

## Installation

1. Copy the `custom_components/pws_fanout` directory to your Home Assistant configuration directory:
   ```
   <config_dir>/custom_components/pws_fanout/
   ```

2. Add the configuration to your `configuration.yaml` file (see below).

3. Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
pws_fanout:
  # Optional: Custom webhook ID (default: "pws_fanout")
  webhook_id: pws_fanout
  
  # Required: List of destinations to forward webhook data to
  destinations:
    - url: http://192.168.0.220:8123/api/webhook/<your key>
      method: POST  # HTTP method: GET or POST (default: POST)
      timeout: 10   # Request timeout in seconds (default: 10)
    
    - url: http://www.bla.com/post.php
      method: POST
      timeout: 15
```

### Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `webhook_id` | string | No | `pws_fanout` | The webhook ID used in the URL |
| `destinations` | list | Yes | - | List of destinations to forward to |
| `destinations[].url` | URL | Yes | - | The URL to forward to |
| `destinations[].method` | string | No | `POST` | HTTP method (`GET` or `POST`) |
| `destinations[].timeout` | int | No | `10` | Request timeout in seconds (1-60) |

## Webhook URL

Once configured, the webhook will be available at:
```
http://<your-ha-address>:8123/api/webhook/<webhook_id>
```

For example, with the default webhook ID:
```
http://192.168.0.100:8123/api/webhook/pws_fanout
```

## Migration from server.py

The original `server.py` ran a standalone HTTP server on port 8123. This integration uses Home Assistant's built-in webhook system, which:

1. Eliminates the need for a separate server
2. Uses Home Assistant's existing web server
3. Leverages Home Assistant's async infrastructure
4. Provides better integration with HA's logging and error handling

### Old server.py configuration:
```python
WEBHOOK_DESTINATIONS = [
    {"url": "http://192.168.0.220:8123/api/webhook/<your key>", "method": "POST"},
    {"url": "http://www.bla.com/post.php", "method": "POST"},
]
```

### New YAML configuration:
```yaml
pws_fanout:
  destinations:
    - url: http://192.168.0.220:8123/api/webhook/asdfasdfasdf
      method: POST
    - url: http://www.bla.com/post.php
      method: POST
```

## Troubleshooting

Check the Home Assistant logs for messages from `pws_fanout`:
- Info: Webhook registration and successful forwarding
- Error: Forwarding failures or timeouts

Enable debug logging in `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.pws_fanout: debug