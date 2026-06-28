package org.poulastaa.birds_eye

import io.ktor.client.HttpClient
import io.ktor.client.engine.darwin.Darwin
import io.ktor.client.plugins.websocket.WebSockets

internal actual fun createDashboardHttpClient(): HttpClient = HttpClient(Darwin) {
    install(WebSockets)
    engine {
        configureRequest {
            setAllowsCellularAccess(true)
        }
    }
}
