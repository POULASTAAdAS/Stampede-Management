package org.poulastaa.birds_eye

import io.ktor.client.HttpClient
import io.ktor.client.engine.okhttp.OkHttp
import io.ktor.client.plugins.websocket.WebSockets

internal actual fun createDashboardHttpClient(): HttpClient = HttpClient(OkHttp) {
    install(WebSockets)
}
