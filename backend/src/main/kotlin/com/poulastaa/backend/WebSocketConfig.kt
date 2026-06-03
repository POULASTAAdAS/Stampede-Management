package com.poulastaa.backend

import org.springframework.context.annotation.Configuration
import org.springframework.web.socket.config.annotation.EnableWebSocket
import org.springframework.web.socket.config.annotation.WebSocketConfigurer
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry

@Configuration
@EnableWebSocket
class WebSocketConfig(
    private val rawMonitoringWebSocketHandler: RawMonitoringWebSocketHandler,
    private val dashboardWebSocketHandler: DashboardWebSocketHandler,
) : WebSocketConfigurer {
    override fun registerWebSocketHandlers(registry: WebSocketHandlerRegistry) {
        // Python monitoring clients send raw JSON payloads here
        registry.addHandler(rawMonitoringWebSocketHandler, "/ws-raw")
            .setAllowedOrigins("*")

        // Browser dashboard clients subscribe to live room updates here
        registry.addHandler(dashboardWebSocketHandler, "/ws-dashboard")
            .setAllowedOrigins("*")
    }
}
