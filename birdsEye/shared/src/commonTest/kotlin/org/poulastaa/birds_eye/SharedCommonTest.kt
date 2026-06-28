package org.poulastaa.birds_eye

import kotlinx.serialization.decodeFromString
import kotlin.test.Test
import kotlin.test.assertEquals

class SharedCommonTest {
    @Test
    fun parsesRoomListPayloadFromDashboardProtocol() {
        val message = DashboardJson.decodeFromString<RoomListMessage>(
            """
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
                      "camera_source": "0"
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
                    }
                  }
                }
              ]
            }
            """.trimIndent(),
        )

        val room = message.rooms.single()
        assertEquals("device:camera-01", room.roomId)
        assertEquals("Main Entrance", room.location())
        assertEquals(3, room.currentCount())
        assertEquals("15:49:14", formatDashboardTime(room.lastSeenAt))
    }

    @Test
    fun filtersRoomsUsingSameFieldsAsWebsiteDashboard() {
        val rooms = listOf(
            RoomSnapshot(
                roomId = "device:camera-01",
                identifierType = "DEVICE_ID",
                identifierValue = "turnstile-east",
                messageCount = 25,
                latestPayload = MonitoringPayload(
                    requestId = "req-entrance-001",
                    capturedAt = "2026-06-24T15:50:00.000Z",
                    deviceInfo = DeviceInfo(
                        deviceId = "camera-01",
                        deviceName = "Entrance Camera",
                        location = "Main Entrance",
                        macAddress = "aa:bb:cc:dd:ee:01",
                        ipAddress = "10.0.0.5",
                    ),
                    populationData = PopulationData(currentCount = 3, alertLevel = "WARNING", alertMessage = "Density approaching capacity"),
                ),
            ),
            RoomSnapshot(
                roomId = "device:camera-02",
                identifierType = "DEVICE_ID",
                identifierValue = "north-exit-sensor",
                latestPayload = MonitoringPayload(
                    deviceInfo = DeviceInfo(
                        deviceId = "camera-02",
                        deviceName = "Exit Camera",
                        location = "North Exit",
                        ipAddress = "10.0.0.6",
                    ),
                    populationData = PopulationData(currentCount = 0, alertLevel = "NORMAL"),
                ),
            ),
        )

        assertEquals(listOf("device:camera-01"), filterRooms(rooms, "entrance warning").map { it.roomId })
        assertEquals(listOf("device:camera-02"), filterRooms(rooms, "north normal").map { it.roomId })
        assertEquals(listOf("device:camera-01"), filterRooms(rooms, "turnstile-east 25").map { it.roomId })
        assertEquals(listOf("device:camera-02"), filterRooms(rooms, "10.0.0.6 normal").map { it.roomId })
    }
}
