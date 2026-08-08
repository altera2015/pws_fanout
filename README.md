# PWS Webhook Fanout - Home Assistant Custom Component

A Home Assistant integration that receives webhook data and forwards it to multiple destinations. This replaces the need for a standalone webhook server.

## Overview

This integration uses Home Assistant's built-in webhook system to receive POST requests and asynchronously forwards them to multiple configured destinations (other Home Assistant instances, external APIs, etc.).

## Features

- **No separate server needed** - Uses Home Assistant's built-in webhook system
- **Async forwarding** - Uses `aiohttp` for non-blocking HTTP requests
- **YAML configuration** - All settings in `configuration.yaml`
- **Multiple destinations** - Forward to as many endpoints as needed
- **Flexible methods** - Support for GET or POST per destination
- **Configurable timeouts** - Set timeout per destination (1-60 seconds)
- **Concurrent forwarding** - All destinations receive data simultaneously

## Installation

### Via HACS (Recommended)

1. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations → ⋮ → Custom repositories
   - Add URL: `https://github.com/altera2015/pws_fanout`
   - Category: Integration
2. Install "PWS Webhook Fanout"
3. Restart Home Assistant

### Manual Installation

1. Copy `custom_components/pws_fanout/` to your Home Assistant config directory:
   ```bash
   cp -r custom_components/pws_fanout /config/custom_components/
   ```
2. Restart Home Assistant

## Configuration

Add to your `configuration.yaml`:

```yaml
pws_fanout:
  # Optional: Custom webhook ID (default: "pws_fanout")
  webhook_id: pws_fanout
  
  # Required: List of destinations to forward webhook data to
  destinations:
    - url: http://192.168.0.220:8123/api/webhook/
      method: POST
      timeout: 10
    
    - url: http://www.example.com/upload.php
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

## Usage

Once configured, send POST requests to:

```
http://<your-ha-address>:8123/api/webhook/<webhook_id>
```

For example:
```bash
curl -X POST "http://192.168.0.100:8123/api/webhook/pws_fanout?station=MYSTATION" \
  -H "Content-Type: application/json" \
  -d '{"temp": 72.5, "humidity": 45}'
```

The data will be forwarded to all configured destinations with the same query parameters and body.

## Migration from server.py

If you were using the standalone `server.py`:

| server.py | HA Integration |
|-----------|----------------|
| Runs on port 8123 | Uses HA's port (usually 8123) |
| Hardcoded destinations | YAML configuration |
| Threading | Async/await |
| Separate process | Part of Home Assistant |

Simply move your destination URLs from the Python file to `configuration.yaml`.

## Troubleshooting

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.pws_fanout: debug
```

Check Home Assistant logs for messages from `pws_fanout`.

## License

MIT License - See [LICENSE](LICENSE) for details.