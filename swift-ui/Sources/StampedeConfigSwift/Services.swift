import AppKit
import AVFoundation
import Darwin
import Foundation

struct ProjectPaths: Sendable {
    var appDirectory: URL

    var mainScript: URL {
        appDirectory.appendingPathComponent("main.py")
    }

    var systemConfig: URL {
        appDirectory.appendingPathComponent("system_conf.json")
    }

    var licenseFile: URL {
        appDirectory.appendingPathComponent("auth/license.dat")
    }

    static func locate() -> ProjectPaths {
        let fileManager = FileManager.default
        let environment = ProcessInfo.processInfo.environment

        if let explicit = environment["STAMPEDE_APP_DIR"], !explicit.isEmpty {
            let url = URL(fileURLWithPath: explicit).standardizedFileURL
            if isProjectDirectory(url, fileManager: fileManager) {
                return ProjectPaths(appDirectory: url)
            }
        }

        var candidates: [URL] = [
            URL(fileURLWithPath: fileManager.currentDirectoryPath).standardizedFileURL
        ]

        if let executable = CommandLine.arguments.first {
            candidates.append(URL(fileURLWithPath: executable).deletingLastPathComponent().standardizedFileURL)
        }

        for candidate in candidates {
            if let located = climbForProjectDirectory(from: candidate, fileManager: fileManager) {
                return ProjectPaths(appDirectory: located)
            }
        }

        return ProjectPaths(appDirectory: candidates[0])
    }

    private static func climbForProjectDirectory(from start: URL, fileManager: FileManager) -> URL? {
        var current = start
        for _ in 0..<12 {
            if isProjectDirectory(current, fileManager: fileManager) {
                return current
            }
            let parent = current.deletingLastPathComponent()
            if parent.path == current.path {
                break
            }
            current = parent
        }
        return nil
    }

    private static func isProjectDirectory(_ url: URL, fileManager: FileManager) -> Bool {
        fileManager.fileExists(atPath: url.appendingPathComponent("main.py").path)
            && fileManager.fileExists(atPath: url.appendingPathComponent("config.py").path)
    }
}

struct PythonEnvironment: Sendable {
    var command: String
    var cv2Available: Bool

    static func resolve(projectDirectory: URL) -> PythonEnvironment {
        let environment = ProcessInfo.processInfo.environment
        if let explicit = environment["STAMPEDE_PYTHON"]?.trimmingCharacters(in: .whitespacesAndNewlines),
           !explicit.isEmpty {
            return PythonEnvironment(
                command: explicit,
                cv2Available: canImportCV2(command: explicit, projectDirectory: projectDirectory)
            )
        }

        let candidates = pythonCandidates(projectDirectory: projectDirectory, environment: environment)
        for candidate in candidates {
            if canImportCV2(command: candidate, projectDirectory: projectDirectory) {
                return PythonEnvironment(command: candidate, cv2Available: true)
            }
        }

        return PythonEnvironment(command: candidates.first ?? "python3", cv2Available: false)
    }

    func requireOpenCV() throws {
        guard cv2Available else {
            throw ServiceError.commandFailed(openCVInstallMessage)
        }
    }

    var openCVInstallMessage: String {
        """
        OpenCV (cv2) is not installed for the Python interpreter selected by the Swift UI:
        \(command)

        Install the project dependencies into a virtual environment, then launch the Swift UI with that interpreter. Example:
        python3 -m venv .venv
        .venv/bin/python -m pip install -r requirements.txt
        STAMPEDE_PYTHON=\"$(pwd)/.venv/bin/python\" swift run --package-path swift-ui StampedeConfigSwift

        If you already have a working Python environment, set STAMPEDE_PYTHON to its python executable.
        """
    }

    private static func pythonCandidates(projectDirectory: URL, environment: [String: String]) -> [String] {
        let fileManager = FileManager.default
        var candidates: [String] = []

        func append(_ command: String) {
            guard !command.isEmpty, !candidates.contains(command) else {
                return
            }
            candidates.append(command)
        }

        func appendIfExecutable(_ url: URL) {
            if fileManager.isExecutableFile(atPath: url.path) {
                append(url.path)
            }
        }

        if let virtualEnv = environment["VIRTUAL_ENV"], !virtualEnv.isEmpty {
            let virtualEnvURL = URL(fileURLWithPath: virtualEnv)
            appendIfExecutable(virtualEnvURL.appendingPathComponent("bin/python3"))
            appendIfExecutable(virtualEnvURL.appendingPathComponent("bin/python"))
        }

        for directory in [".venv", "venv", "env", "ENV"] {
            let virtualEnvURL = projectDirectory.appendingPathComponent(directory)
            appendIfExecutable(virtualEnvURL.appendingPathComponent("bin/python3"))
            appendIfExecutable(virtualEnvURL.appendingPathComponent("bin/python"))
        }

        append("python3")
        append("python")
        appendIfExecutable(URL(fileURLWithPath: "/opt/homebrew/bin/python3"))
        appendIfExecutable(URL(fileURLWithPath: "/usr/local/bin/python3"))
        appendIfExecutable(URL(fileURLWithPath: "/usr/bin/python3"))
        appendIfExecutable(URL(fileURLWithPath: "/Applications/Xcode.app/Contents/Developer/usr/bin/python3"))

        return candidates
    }

    private static func canImportCV2(command: String, projectDirectory: URL) -> Bool {
        do {
            let result = try ProcessRunner().runEnv(
                arguments: [command, "-c", "import cv2"],
                currentDirectory: projectDirectory,
                timeout: 8
            )
            return result.exitCode == 0
        } catch {
            return false
        }
    }
}

struct PermissionService: Sendable {
    static func requestAudioAccessAtStartup() {
        guard AVCaptureDevice.authorizationStatus(for: .audio) == .notDetermined else {
            return
        }

        AVCaptureDevice.requestAccess(for: .audio) { _ in }
    }
}

struct CommandResult: Sendable {
    var stdout: String
    var stderr: String
    var exitCode: Int32
}

enum CommandError: LocalizedError, Sendable {
    case timedOut(String)
    case failedToStart(String)

    var errorDescription: String? {
        switch self {
        case let .timedOut(command):
            return "Command timed out: \(command)"
        case let .failedToStart(message):
            return message
        }
    }
}

struct ProcessRunner: Sendable {
    func runEnv(arguments: [String], currentDirectory: URL, timeout: TimeInterval = 30) throws -> CommandResult {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = arguments
        process.currentDirectoryURL = currentDirectory

        let stdout = Pipe()
        let stderr = Pipe()
        process.standardOutput = stdout
        process.standardError = stderr

        do {
            try process.run()
        } catch {
            throw CommandError.failedToStart(error.localizedDescription)
        }

        let semaphore = DispatchSemaphore(value: 0)
        DispatchQueue.global(qos: .utility).async {
            process.waitUntilExit()
            semaphore.signal()
        }

        if semaphore.wait(timeout: .now() + timeout) == .timedOut {
            process.terminate()
            return try readResult(process: process, stdout: stdout, stderr: stderr, timedOutCommand: arguments.joined(separator: " "))
        }

        return try readResult(process: process, stdout: stdout, stderr: stderr, timedOutCommand: nil)
    }

    private func readResult(process: Process, stdout: Pipe, stderr: Pipe, timedOutCommand: String?) throws -> CommandResult {
        let stdoutData = stdout.fileHandleForReading.readDataToEndOfFile()
        let stderrData = stderr.fileHandleForReading.readDataToEndOfFile()
        if let timedOutCommand {
            throw CommandError.timedOut(timedOutCommand)
        }
        return CommandResult(
            stdout: String(data: stdoutData, encoding: .utf8) ?? "",
            stderr: String(data: stderrData, encoding: .utf8) ?? "",
            exitCode: process.terminationStatus
        )
    }
}

enum ServiceError: LocalizedError, Sendable {
    case commandFailed(String)
    case invalidJSON(String)
    case licenseMismatch(String)
    case emptyLicense
    case invalidLicense(String)

    var errorDescription: String? {
        switch self {
        case let .commandFailed(message):
            return message
        case let .invalidJSON(message):
            return "Invalid JSON: \(message)"
        case let .licenseMismatch(message):
            return message
        case .emptyLicense:
            return "Please enter a license key."
        case let .invalidLicense(message):
            return "License validation failed: \(message)"
        }
    }
}

struct LicenseService: Sendable {
    var paths: ProjectPaths
    var python: PythonEnvironment
    var runner = ProcessRunner()

    func status() throws -> LicenseStatus {
        let result = try runner.runEnv(
            arguments: [python.command, "-c", Self.statusScript],
            currentDirectory: paths.appDirectory,
            timeout: 15
        )
        guard result.exitCode == 0 else {
            throw ServiceError.commandFailed(result.stderr.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? result.stdout : result.stderr)
        }
        guard let data = result.stdout.data(using: .utf8) else {
            throw ServiceError.invalidJSON("License helper returned non-UTF8 output.")
        }
        do {
            return try JSONDecoder().decode(LicenseStatus.self, from: data)
        } catch {
            throw ServiceError.invalidJSON(error.localizedDescription)
        }
    }

    func activate(licenseText: String) throws -> LicenseStatus {
        let trimmed = licenseText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            throw ServiceError.emptyLicense
        }

        let currentStatus = try status()
        let machineInfo = currentStatus.currentMachineInfo
        let data = Data(trimmed.utf8)
        let object: [String: Any]
        do {
            guard let parsed = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                throw ServiceError.invalidJSON("License key must be a JSON object.")
            }
            object = parsed
        } catch let error as ServiceError {
            throw error
        } catch {
            throw ServiceError.invalidJSON(error.localizedDescription)
        }

        let licenseMachineID = object["machine_id"] as? String ?? ""
        let licenseMAC = object["mac_address"] as? String ?? ""
        let licenseUsername = object["username"] as? String ?? ""

        guard licenseMachineID == machineInfo.machineID else {
            throw ServiceError.licenseMismatch(
                "This license is for a different machine.\n\nExpected Machine ID: \(machineInfo.machineID)\nLicense Machine ID: \(licenseMachineID)"
            )
        }
        guard licenseMAC.uppercased() == machineInfo.macAddress.uppercased() else {
            throw ServiceError.licenseMismatch(
                "This license is for a different MAC address.\n\nYour MAC Address: \(machineInfo.macAddress)\nLicense MAC Address: \(licenseMAC)"
            )
        }
        guard licenseUsername == machineInfo.username else {
            throw ServiceError.licenseMismatch(
                "This license is for a different username.\n\nYour Username: \(machineInfo.username)\nLicense Username: \(licenseUsername)"
            )
        }

        try FileManager.default.createDirectory(
            at: paths.licenseFile.deletingLastPathComponent(),
            withIntermediateDirectories: true
        )
        try trimmed.write(to: paths.licenseFile, atomically: true, encoding: .utf8)

        let newStatus = try status()
        guard newStatus.valid else {
            throw ServiceError.invalidLicense(newStatus.message)
        }
        return newStatus
    }

    private static let statusScript = #"""
import json
import os
import sys
from pathlib import Path

app_dir = Path.cwd()
sys.path.insert(0, str(app_dir))
from auth.license_manager import LicenseManager

manager = LicenseManager(str(app_dir / "auth" / "license.dat"))
valid, message = manager.validate_license()
license_data = manager.load_license() or {}
info = manager.get_license_info() or {}
username = os.getenv("USERNAME") or os.getenv("USER") or "unknown"

payload = {
    "valid": bool(valid),
    "message": message,
    "customer_name": info.get("customer_name") or license_data.get("customer_name"),
    "created": info.get("created") or license_data.get("created"),
    "expires": info.get("expires") or license_data.get("expires"),
    "machine_id": info.get("machine_id") or license_data.get("machine_id"),
    "mac_address": license_data.get("mac_address"),
    "username": license_data.get("username"),
    "days_remaining": info.get("days_remaining"),
    "current_machine_id": manager.get_machine_id(),
    "current_mac_address": manager.get_mac_address(),
    "current_username": username,
}
print(json.dumps(payload))
"""#
}

struct CameraDetectionService: Sendable {
    var paths: ProjectPaths
    var python: PythonEnvironment
    var runner = ProcessRunner()

    func detect(maxCameras: Int = 10) throws -> [CameraInfo] {
        try python.requireOpenCV()

        let script = Self.cameraScript.replacingOccurrences(of: "MAX_CAMERAS", with: String(maxCameras))
        let result = try runner.runEnv(
            arguments: [python.command, "-c", script],
            currentDirectory: paths.appDirectory,
            timeout: 30
        )
        guard result.exitCode == 0 else {
            let message = result.stderr.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                ? result.stdout
                : result.stderr
            if message.contains("No module named 'cv2'") || message.contains("No module named cv2") {
                throw ServiceError.commandFailed(python.openCVInstallMessage)
            }
            throw ServiceError.commandFailed(message.trimmingCharacters(in: .whitespacesAndNewlines))
        }

        guard let data = result.stdout.data(using: .utf8) else {
            throw ServiceError.invalidJSON("Camera helper returned non-UTF8 output.")
        }
        do {
            return try JSONDecoder().decode([CameraInfo].self, from: data)
        } catch {
            throw ServiceError.invalidJSON(error.localizedDescription)
        }
    }

    private static let cameraScript = #"""
import json
import platform

import cv2


def open_video_capture(source):
    avfoundation = getattr(cv2, "CAP_AVFOUNDATION", None)
    if isinstance(source, int) and platform.system() == "Darwin" and avfoundation is not None:
        cap = cv2.VideoCapture(source, avfoundation)
        if cap.isOpened():
            return cap
        cap.release()
    return cv2.VideoCapture(source)


cameras = []
for index in range(MAX_CAMERAS):
    cap = None
    try:
        cap = open_video_capture(index)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cameras.append({
                    "index": index,
                    "name": f"Camera {index} ({width}x{height})",
                    "width": width,
                    "height": height,
                })
    except Exception:
        pass
    finally:
        if cap is not None:
            cap.release()

print(json.dumps(cameras))
"""#
}

@MainActor
enum Dialogs {
    static func info(title: String, message: String) {
        show(title: title, message: message, style: .informational)
    }

    static func warning(title: String, message: String) {
        show(title: title, message: message, style: .warning)
    }

    static func error(title: String, message: String) {
        show(title: title, message: message, style: .critical)
    }

    static func confirm(title: String, message: String) -> Bool {
        let alert = NSAlert()
        alert.messageText = title
        alert.informativeText = message
        alert.alertStyle = .warning
        alert.addButton(withTitle: "Yes")
        alert.addButton(withTitle: "No")
        return alert.runModal() == .alertFirstButtonReturn
    }

    private static func show(title: String, message: String, style: NSAlert.Style) {
        let alert = NSAlert()
        alert.messageText = title
        alert.informativeText = message
        alert.alertStyle = style
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }
}
