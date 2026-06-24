# Dashboard WebSocket API

This document describes how to connect to the public dashboard WebSocket endpoint:

```text
wss://stamped.poulastaa.dev/ws-dashboard
```

This endpoint is for dashboard clients that want to list rooms and subscribe to live room updates.

It is not the endpoint for Python monitoring devices to publish crowd data. Python monitoring devices should publish raw
monitoring payloads to:

```text
wss://stamped.poulastaa.dev/ws-raw
```

## Endpoint Summary

| Purpose                                               | Endpoint                                   |
|-------------------------------------------------------|--------------------------------------------|
| Dashboard clients receive room lists and room updates | `wss://stamped.poulastaa.dev/ws-dashboard` |
| Python/device clients send monitoring payloads        | `wss://stamped.poulastaa.dev/ws-raw`       |
| Local dashboard endpoint on this Mac                  | `ws://localhost:9990/ws-dashboard`         |
| Local raw monitoring endpoint on this Mac             | `ws://localhost:9990/ws-raw`               |

## Dashboard Connection Flow

1. Open a WebSocket connection to `wss://stamped.poulastaa.dev/ws-dashboard`.
2. The backend immediately sends a `room_list` message.
3. Send `{"action":"list"}` any time you need the latest room list.
4. Pick a `roomId` from the `rooms` array.
5. Send `{"action":"subscribe","roomId":"..."}` to receive live updates for that room.
6. Send `{"action":"unsubscribe","roomId":"..."}` to stop receiving updates for that room.

## Client Messages

All client messages must be JSON text messages.

### List Rooms

Request the latest known rooms.

```json
{
  "action": "list"
}
```

Required fields:

| Field    | Type   | Required | Description     |
|----------|--------|----------|-----------------|
| `action` | string | yes      | Must be `list`. |

### Subscribe To A Room

Subscribe to live updates for one room.

```json
{
  "action": "subscribe",
  "roomId": "device:camera-01"
}
```

Required fields:

| Field    | Type   | Required | Description                                   |
|----------|--------|----------|-----------------------------------------------|
| `action` | string | yes      | Must be `subscribe`.                          |
| `roomId` | string | yes      | Room ID returned by the `room_list` response. |

Valid `roomId` values are created by the raw monitoring endpoint from the device identifier:

| Identifier source                                    | Resulting `roomId` format | Example                 |
|------------------------------------------------------|---------------------------|-------------------------|
| `device_info.device_id` or top-level `device_id`     | `device:<device_id>`      | `device:camera-01`      |
| `device_info.mac_address` or top-level `mac_address` | `mac:<normalized_mac>`    | `mac:aa:bb:cc:dd:ee:ff` |

Use the exact `roomId` value from the `room_list` response instead of constructing it manually when possible.

### Unsubscribe From A Room

Stop receiving live updates for a room.

```json
{
  "action": "unsubscribe",
  "roomId": "device:camera-01"
}
```

Required fields:

| Field    | Type   | Required | Description                  |
|----------|--------|----------|------------------------------|
| `action` | string | yes      | Must be `unsubscribe`.       |
| `roomId` | string | yes      | Room ID to unsubscribe from. |

## Server Messages

### Room List

The server sends this immediately after connection and whenever room metadata changes.

```json
{
  "type": "room_list",
  "rooms": [
    {
      "roomId": "device:camera-01",
      "identifierType": "DEVICE_ID",
      "identifierValue": "camera-01",
      "createdAt": "2026-06-24T15:48:14.000Z",
      "lastSeenAt": "2026-06-24T15:49:14.000Z",
      "messageCount": 12,
      "latestPayload": {
        "device_info": {
          "device_id": "camera-01",
          "device_name": "Entrance Camera",
          "location": "Main Entrance",
          "camera_source": "0",
          "mac_address": "aa:bb:cc:dd:ee:ff",
          "ip_address": "192.168.1.50",
          "timestamp": "2026-06-24T15:49:14.000Z"
        },
        "population_data": {
          "current_count": 3,
          "tracked_persons": [],
          "occupancy_grid": {
            "rows": 5,
            "cols": 5,
            "cells": [],
            "total_occupants": 3,
            "average_density": 0.12
          },
          "alert_level": "NORMAL",
          "alert_message": null,
          "frame_number": 120,
          "fps": 14.9
        },
        "request_id": "4c2d2a41-2f82-49f2-b956-a34510f2f89f",
        "captured_at": "2026-06-24T15:49:14.000Z"
      }
    }
  ]
}
```

Fields:

| Field                     | Type           | Description                                                                           |
|---------------------------|----------------|---------------------------------------------------------------------------------------|
| `type`                    | string         | Always `room_list`.                                                                   |
| `rooms`                   | array          | Known rooms/devices. Empty array means no Python monitoring device has sent data yet. |
| `rooms[].roomId`          | string         | ID used for `subscribe` and `unsubscribe`.                                            |
| `rooms[].identifierType`  | string         | `DEVICE_ID` or `MAC_ADDRESS`.                                                         |
| `rooms[].identifierValue` | string         | Original device ID or MAC address value.                                              |
| `rooms[].createdAt`       | string         | ISO timestamp when the room was first seen.                                           |
| `rooms[].lastSeenAt`      | string         | ISO timestamp when the room last sent data.                                           |
| `rooms[].messageCount`    | number         | Count of payloads received for the room.                                              |
| `rooms[].latestPayload`   | object or null | Most recent raw monitoring payload for the room, parsed as JSON.                      |

### Subscribe Confirmation

Sent after a successful subscribe request.

```json
{
  "type": "subscribed",
  "roomId": "device:camera-01"
}
```

### Room Update

Sent to clients subscribed to a room whenever that room receives a new monitoring payload through `/ws-raw`.

```json
{
  "type": "room_update",
  "roomId": "device:camera-01",
  "data": {
    "device_info": {
      "device_id": "camera-01",
      "device_name": "Entrance Camera",
      "location": "Main Entrance",
      "camera_source": "0",
      "mac_address": "aa:bb:cc:dd:ee:ff",
      "ip_address": "192.168.1.50",
      "timestamp": "2026-06-24T15:49:14.000Z"
    },
    "population_data": {
      "current_count": 3,
      "tracked_persons": [
        {
          "track_id": 1,
          "bounding_box": {
            "x": 120,
            "y": 80,
            "width": 40,
            "height": 90
          },
          "confidence": 0.91,
          "age": 8,
          "confirmed": true,
          "world_x": 2.4,
          "world_y": 5.1
        }
      ],
      "occupancy_grid": {
        "rows": 5,
        "cols": 5,
        "cells": [
          {
            "row": 0,
            "col": 0,
            "occupant_count": 1.0,
            "density": 0.2,
            "alert_level": "NORMAL"
          }
        ],
        "total_occupants": 3,
        "average_density": 0.12
      },
      "alert_level": "NORMAL",
      "alert_message": null,
      "frame_number": 120,
      "fps": 14.9
    },
    "request_id": "4c2d2a41-2f82-49f2-b956-a34510f2f89f",
    "captured_at": "2026-06-24T15:49:14.000Z"
  }
}
```

Fields:

| Field    | Type           | Description                                           |
|----------|----------------|-------------------------------------------------------|
| `type`   | string         | Always `room_update`.                                 |
| `roomId` | string         | Room that produced the update.                        |
| `data`   | object or null | Latest monitoring payload parsed from the raw sender. |

### Error Message

The dashboard endpoint can return these errors:

```json
{
  "type": "error",
  "message": "invalid_json"
}
```

Possible `message` values:

| Message          | Cause                                                                     |
|------------------|---------------------------------------------------------------------------|
| `invalid_json`   | The WebSocket message was not valid JSON.                                 |
| `missing_roomId` | A `subscribe` request did not include a non-empty `roomId`.               |
| `unknown_action` | `action` was missing or not one of `list`, `subscribe`, or `unsubscribe`. |

## JavaScript Example

```js
const ws = new WebSocket('wss://stamped.poulastaa.dev/ws-dashboard')

ws.addEventListener('open', () => {
  ws.send(JSON.stringify({ action: 'list' }))
})

ws.addEventListener('message', (event) => {
  const message = JSON.parse(event.data)

  if (message.type === 'room_list') {
    const firstRoom = message.rooms[0]

    if (firstRoom) {
      ws.send(JSON.stringify({
        action: 'subscribe',
        roomId: firstRoom.roomId,
      }))
    }
  }

  if (message.type === 'room_update') {
    console.log('Room update:', message.roomId, message.data)
  }

  if (message.type === 'error') {
    console.error('Dashboard WebSocket error:', message.message)
  }
})
```

## Python Dashboard Client Example

Install:

```sh
pip install websocket-client
```

Example:

```python
import json
import websocket

url = "wss://stamped.poulastaa.dev/ws-dashboard"


def on_open(ws):
    ws.send(json.dumps({"action": "list"}))


def on_message(ws, raw_message):
    message = json.loads(raw_message)
    print(message)

    if message.get("type") == "room_list" and message.get("rooms"):
        room_id = message["rooms"][0]["roomId"]
        ws.send(json.dumps({"action": "subscribe", "roomId": room_id}))


ws = websocket.WebSocketApp(
    url,
    on_open=on_open,
    on_message=on_message,
)

ws.run_forever(ping_interval=20, ping_timeout=10)
```

## Sending Monitoring Data

Do not send monitoring payloads to `/ws-dashboard`. The dashboard endpoint will reject them with `unknown_action`
because monitoring payloads do not contain one of the supported dashboard `action` values.

Send monitoring data to:

```text
wss://stamped.poulastaa.dev/ws-raw
```

Minimum accepted raw payload:

```json
{
  "device_info": {
    "device_id": "camera-01",
    "device_name": "Entrance Camera",
    "location": "Main Entrance",
    "camera_source": "0",
    "mac_address": "aa:bb:cc:dd:ee:ff"
  },
  "population_data": {
    "current_count": 3,
    "tracked_persons": [],
    "occupancy_grid": {
      "rows": 5,
      "cols": 5,
      "cells": [],
      "total_occupants": 3,
      "average_density": 0.12
    },
    "alert_level": "NORMAL",
    "alert_message": null,
    "frame_number": 120,
    "fps": 14.9
  },
  "request_id": "4c2d2a41-2f82-49f2-b956-a34510f2f89f",
  "captured_at": "2026-06-24T15:49:14.000Z"
}
```

The raw endpoint requires at least one of these identifiers:

| Accepted identifier | JSON path                                            |
|---------------------|------------------------------------------------------|
| Device ID           | `device_info.device_id` or top-level `device_id`     |
| MAC address         | `device_info.mac_address` or top-level `mac_address` |

Raw endpoint success response:

```json
{
  "status": "accepted",
  "request_id": "4c2d2a41-2f82-49f2-b956-a34510f2f89f",
  "room_id": "device:camera-01"
}
```

Raw endpoint rejection responses:

```json
{
  "status": "rejected",
  "reason": "invalid_json"
}
```

```json
{
  "status": "rejected",
  "reason": "missing_device_id_or_mac"
}
```
