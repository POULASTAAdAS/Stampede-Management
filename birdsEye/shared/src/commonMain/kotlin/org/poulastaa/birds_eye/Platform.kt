package org.poulastaa.birds_eye

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform