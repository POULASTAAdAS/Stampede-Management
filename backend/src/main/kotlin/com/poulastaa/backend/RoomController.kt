package com.poulastaa.backend

import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/rooms")
class RoomController(
    private val roomRegistry: RoomRegistry,
) {
    @GetMapping
    fun listRooms(): List<Room> = roomRegistry.listRooms()
}
