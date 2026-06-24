import Foundation

enum SourceValue: Codable, Equatable, Sendable {
    case int(Int)
    case string(String)

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let value = try? container.decode(Int.self) {
            self = .int(value)
            return
        }
        self = .string(try container.decode(String.self))
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case let .int(value):
            try container.encode(value)
        case let .string(value):
            try container.encode(value)
        }
    }

    var cameraIndex: Int? {
        switch self {
        case let .int(value):
            return value
        case let .string(value):
            return Int(value)
        }
    }

    var stringValue: String {
        switch self {
        case let .int(value):
            return String(value)
        case let .string(value):
            return value
        }
    }
}

struct MonitoringConfig: Codable, Equatable, Sendable {
    var source: SourceValue = .string("0")
    var model_path: String = "model/yolov8n.pt"

    var camera_width: Int = 1280
    var camera_height: Int = 720
    var camera_fps: Int = 30

    var cell_width: Double = 1.0
    var cell_height: Double = 1.0
    var person_radius: Double = 2.0

    var detect_every: Int = 5
    var confidence_threshold: Double = 0.35
    var min_bbox_area: Int = 1500
    var yolo_imgsz: Int = 640

    var use_deepsort: Bool = false
    var max_age: Int = 80
    var n_init: Int = 1
    var centroid_distance_threshold: Double = 80.0

    var ema_alpha: Double = 0.4
    var fps: Double = 15.0
    var hysteresis_time: Double = 3.0
    var alert_clear_offset: Double = 0.5
    var occupancy_warning_threshold: Double = 0.8

    var max_birdseye_pixels: Int = 900
    var grid_line_thickness: Int = 2
    var bbox_thickness: Int = 3
    var info_panel_height: Int = 120
    var font_size_large: Double = 0.8
    var font_size_medium: Double = 0.6
    var font_size_small: Double = 0.5
    var font_size_tiny: Double = 0.4
    var font_size_birdseye: Double = 0.35

    var enable_screenshots: Bool = true
    var enable_grid_adjustment: Bool = true
    var fps_counter_window: Int = 30
    var split_view_divisor: Int = 2

    var calibration_area_width: Double = 10.0
    var calibration_area_height: Double = 10.0
    var auto_calibration: Bool = false
    var calibration_point_radius: Int = 8
    var calibration_line_thickness: Int = 2

    var websocket_enabled: Bool = true
    var websocket_request_enabled: Bool = true
    var websocket_log_flow: Bool = true
    var websocket_url: String = "wss://stamped.poulastaa.dev/ws-raw"
    var websocket_device_id: String = ""
    var websocket_mac_address: String = ""
    var websocket_device_name: String = ""
    var websocket_location: String = "Unknown Location"
    var websocket_debounce_seconds: Double = 3.0

    mutating func apply(jsonObject object: [String: Any]) {
        if let rawSource = object["source"] {
            if let number = rawSource as? NSNumber, !(rawSource is Bool) {
                source = .int(number.intValue)
            } else if let value = rawSource as? String {
                source = .string(value)
            }
        }

        updateString(&model_path, key: "model_path", object: object)
        updateInt(&camera_width, key: "camera_width", object: object)
        updateInt(&camera_height, key: "camera_height", object: object)
        updateInt(&camera_fps, key: "camera_fps", object: object)

        updateDouble(&cell_width, key: "cell_width", object: object)
        updateDouble(&cell_height, key: "cell_height", object: object)
        updateDouble(&person_radius, key: "person_radius", object: object)

        updateInt(&detect_every, key: "detect_every", object: object)
        updateDouble(&confidence_threshold, key: "confidence_threshold", object: object)
        updateInt(&min_bbox_area, key: "min_bbox_area", object: object)
        updateInt(&yolo_imgsz, key: "yolo_imgsz", object: object)

        updateBool(&use_deepsort, key: "use_deepsort", object: object)
        updateInt(&max_age, key: "max_age", object: object)
        updateInt(&n_init, key: "n_init", object: object)
        updateDouble(&centroid_distance_threshold, key: "centroid_distance_threshold", object: object)

        updateDouble(&ema_alpha, key: "ema_alpha", object: object)
        updateDouble(&fps, key: "fps", object: object)
        updateDouble(&hysteresis_time, key: "hysteresis_time", object: object)
        updateDouble(&alert_clear_offset, key: "alert_clear_offset", object: object)
        updateDouble(&occupancy_warning_threshold, key: "occupancy_warning_threshold", object: object)

        updateInt(&max_birdseye_pixels, key: "max_birdseye_pixels", object: object)
        updateInt(&grid_line_thickness, key: "grid_line_thickness", object: object)
        updateInt(&bbox_thickness, key: "bbox_thickness", object: object)
        updateInt(&info_panel_height, key: "info_panel_height", object: object)
        updateDouble(&font_size_large, key: "font_size_large", object: object)
        updateDouble(&font_size_medium, key: "font_size_medium", object: object)
        updateDouble(&font_size_small, key: "font_size_small", object: object)
        updateDouble(&font_size_tiny, key: "font_size_tiny", object: object)
        updateDouble(&font_size_birdseye, key: "font_size_birdseye", object: object)

        updateBool(&enable_screenshots, key: "enable_screenshots", object: object)
        updateBool(&enable_grid_adjustment, key: "enable_grid_adjustment", object: object)
        updateInt(&fps_counter_window, key: "fps_counter_window", object: object)
        updateInt(&split_view_divisor, key: "split_view_divisor", object: object)

        updateDouble(&calibration_area_width, key: "calibration_area_width", object: object)
        updateDouble(&calibration_area_height, key: "calibration_area_height", object: object)
        updateBool(&auto_calibration, key: "auto_calibration", object: object)
        updateInt(&calibration_point_radius, key: "calibration_point_radius", object: object)
        updateInt(&calibration_line_thickness, key: "calibration_line_thickness", object: object)

        updateBool(&websocket_enabled, key: "websocket_enabled", object: object)
        updateBool(&websocket_request_enabled, key: "websocket_request_enabled", object: object)
        updateBool(&websocket_log_flow, key: "websocket_log_flow", object: object)
        updateString(&websocket_url, key: "websocket_url", object: object)
        updateString(&websocket_device_id, key: "websocket_device_id", object: object)
        updateString(&websocket_mac_address, key: "websocket_mac_address", object: object)
        updateString(&websocket_device_name, key: "websocket_device_name", object: object)
        updateString(&websocket_location, key: "websocket_location", object: object)
        updateDouble(&websocket_debounce_seconds, key: "websocket_debounce_seconds", object: object)
    }
}

private func updateString(_ field: inout String, key: String, object: [String: Any]) {
    if let value = object[key] as? String {
        field = value
    }
}

private func updateInt(_ field: inout Int, key: String, object: [String: Any]) {
    guard let raw = object[key] else {
        return
    }
    if let value = raw as? Int {
        field = value
    } else if let number = raw as? NSNumber, !(raw is Bool) {
        field = number.intValue
    } else if let value = raw as? String, let doubleValue = Double(value) {
        field = Int(doubleValue)
    }
}

private func updateDouble(_ field: inout Double, key: String, object: [String: Any]) {
    guard let raw = object[key] else {
        return
    }
    if let value = raw as? Double {
        field = value
    } else if let number = raw as? NSNumber, !(raw is Bool) {
        field = number.doubleValue
    } else if let value = raw as? String, let doubleValue = Double(value) {
        field = doubleValue
    }
}

private func updateBool(_ field: inout Bool, key: String, object: [String: Any]) {
    guard let raw = object[key] else {
        return
    }
    if let value = raw as? Bool {
        field = value
    } else if let number = raw as? NSNumber {
        field = number.boolValue
    } else if let value = raw as? String {
        let normalized = value.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if ["true", "1", "yes", "y"].contains(normalized) {
            field = true
        } else if ["false", "0", "no", "n"].contains(normalized) {
            field = false
        }
    }
}

struct CameraInfo: Codable, Hashable, Sendable {
    var index: Int
    var name: String
    var width: Int
    var height: Int
}

struct MachineInfo: Equatable, Sendable {
    var machineID: String
    var macAddress: String
    var username: String
}

struct LicenseStatus: Decodable, Sendable {
    var valid: Bool
    var message: String
    var customer_name: String?
    var created: String?
    var expires: String?
    var machine_id: String?
    var mac_address: String?
    var username: String?
    var days_remaining: Int?
    var current_machine_id: String
    var current_mac_address: String
    var current_username: String

    var currentMachineInfo: MachineInfo {
        MachineInfo(
            machineID: current_machine_id,
            macAddress: current_mac_address,
            username: current_username
        )
    }
}
