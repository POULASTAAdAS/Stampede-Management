package com.poulastaa.backend

import tools.jackson.databind.ObjectMapper
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest

@SpringBootTest
class BackendApplicationTests @Autowired constructor(
    private val rawMonitoringWebSocketHandler: RawMonitoringWebSocketHandler,
    private val objectMapper: ObjectMapper,
) {

    @Test
    fun contextLoads() {
    }

    @Test
    fun `normalizes stale critical cell when density is back under capacity`() {
        val payload = monitoringPayload(alertLevel = "CRITICAL", cellAlertLevel = "CRITICAL", density = 0.4)

        val normalized = rawMonitoringWebSocketHandler.normalizeMonitoringPayload(objectMapper.readTree(payload))

        assertEquals("NORMAL", normalized.at("/population_data/alert_level").asText())
        assertTrue(normalized.at("/population_data/alert_message").isNull)
        assertEquals("NORMAL", normalized.at("/population_data/occupancy_grid/cells/0/alert_level").asText())
    }

    @Test
    fun `keeps true critical cell when density is at capacity`() {
        val payload = monitoringPayload(alertLevel = "CRITICAL", cellAlertLevel = "CRITICAL", density = 1.0)

        val normalized = rawMonitoringWebSocketHandler.normalizeMonitoringPayload(objectMapper.readTree(payload))

        assertEquals("CRITICAL", normalized.at("/population_data/alert_level").asText())
        assertEquals("CRITICAL", normalized.at("/population_data/occupancy_grid/cells/0/alert_level").asText())
    }

    private fun monitoringPayload(alertLevel: String, cellAlertLevel: String, density: Double): String =
        """
        {
          "device_info": {
            "device_id": "camera-01",
            "device_name": "Camera 01"
          },
          "population_data": {
            "current_count": 1,
            "tracked_persons": [],
            "occupancy_grid": {
              "rows": 1,
              "cols": 1,
              "cells": [
                {
                  "row": 0,
                  "col": 0,
                  "occupant_count": 0.4,
                  "density": $density,
                  "alert_level": "$cellAlertLevel"
                }
              ],
              "total_occupants": 1,
              "average_density": $density
            },
            "alert_level": "$alertLevel",
            "alert_message": "CRITICAL: Overcapacity detected in one or more grid cells.",
            "frame_number": 1,
            "fps": 15.0
          },
          "request_id": "test-request",
          "captured_at": "2026-06-24T15:49:14.000Z"
        }
        """.trimIndent()

}
