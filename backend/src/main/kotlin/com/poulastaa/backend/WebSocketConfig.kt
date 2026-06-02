package com.poulastaa.backend

import org.springframework.context.annotation.Configuration
import org.springframework.web.socket.config.annotation.EnableWebSocket
import org.springframework.web.socket.config.annotation.WebSocketConfigurer
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry

@Configuration
@EnableWebSocket
class WebSocketConfig(
    private val rawMonitoringWebSocketHandler: RawMonitoringWebSocketHandler,
) : WebSocketConfigurer {
    override fun registerWebSocketHandlers(registry: WebSocketHandlerRegistry) {
        registry.addHandler(rawMonitoringWebSocketHandler, "/ws-raw")
            .setAllowedOrigins("*")
    }
}
