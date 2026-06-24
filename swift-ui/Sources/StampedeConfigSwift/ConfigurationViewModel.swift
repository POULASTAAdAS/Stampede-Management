import AppKit
import Darwin
import Foundation
import UniformTypeIdentifiers

@MainActor
final class ConfigurationViewModel: ObservableObject {
    let paths: ProjectPaths
    let python: PythonEnvironment
    private let licenseService: LicenseService
    private let cameraService: CameraDetectionService

    @Published var config = MonitoringConfig()
    @Published var sourceOptions: [String] = []
    @Published var selectedSourceOption = ""
    @Published var cameraStatusText = "Detecting cameras..."
    @Published var cameraStatusKind: StatusKind = .info
    @Published var statusText = "Ready"
    @Published var licenseStatusText = "License: Unknown"
    @Published var isDetectingCameras = false
    @Published var camerasDetected = false
    @Published var monitorIsRunning = false
    @Published var showActivation = false
    @Published var activationMachineInfo = MachineInfo(machineID: "", macAddress: "", username: "")

    private var didStart = false
    private var startupFinished = false
    private var availableCameras: [CameraInfo] = []
    private var suppressNextSourceChange = false
    private var monitorProcess: Process?
    private var monitorPID: Int32?
    private var monitorConfigURL: URL?
    private var stopRequested = false
    private var licenseTimer: Timer?

    var canRunMonitor: Bool {
        camerasDetected && !monitorIsRunning && !isDetectingCameras
    }

    init() {
        let resolvedPaths = ProjectPaths.locate()
        let resolvedPython = PythonEnvironment.resolve(projectDirectory: resolvedPaths.appDirectory)
        paths = resolvedPaths
        python = resolvedPython
        licenseService = LicenseService(paths: resolvedPaths, python: resolvedPython)
        cameraService = CameraDetectionService(paths: resolvedPaths, python: resolvedPython)
    }

    func startIfNeeded() {
        guard !didStart else {
            return
        }
        didStart = true

        PermissionService.requestAudioAccessAtStartup()

        guard FileManager.default.fileExists(atPath: paths.mainScript.path) else {
            Dialogs.error(
                title: "Project Not Found",
                message: "Could not locate main.py. Set STAMPEDE_APP_DIR to the Stampede-Management project directory."
            )
            return
        }

        do {
            let status = try licenseService.status()
            activationMachineInfo = status.currentMachineInfo
            updateLicenseStatus(status)
            guard status.valid else {
                Dialogs.warning(title: "License Required", message: status.message)
                showActivation = true
                return
            }
            if let days = status.days_remaining, days < 30 {
                Dialogs.warning(
                    title: "License Expiring Soon",
                    message: "Your license will expire in \(days) days. Please renew soon."
                )
            }
            finishStartup()
        } catch {
            Dialogs.error(title: "License Error", message: error.localizedDescription)
            showActivation = true
        }
    }

    func handleActivationExit() {
        NSApplication.shared.terminate(nil)
    }

    func copyMachineInfo() {
        let info = "Machine ID: \(activationMachineInfo.machineID)\nMAC Address: \(activationMachineInfo.macAddress)\nUsername: \(activationMachineInfo.username)"
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(info, forType: .string)
        Dialogs.info(
            title: "Copied",
            message: "Machine information copied to clipboard. Send this to support to request your license."
        )
    }

    func activateLicense(_ licenseText: String) {
        do {
            let status = try licenseService.activate(licenseText: licenseText)
            activationMachineInfo = status.currentMachineInfo
            updateLicenseStatus(status)
            showActivation = false
            Dialogs.info(title: "Success", message: "License activated successfully.")
            finishStartup()
        } catch {
            Dialogs.error(title: "Activation Failed", message: error.localizedDescription)
        }
    }

    func showLicenseInfo() {
        do {
            let status = try licenseService.status()
            updateLicenseStatus(status)
            let licenseMAC = status.mac_address ?? status.current_mac_address
            let username = status.username ?? status.current_username
            let machineID = status.machine_id ?? status.current_machine_id
            let message = """
            License Information:

            Customer: \(status.customer_name ?? "N/A")
            MAC Address: \(licenseMAC)
            Username: \(username)
            Created: \(status.created ?? "Unknown")
            Expires: \(status.expires ?? "Unknown")
            Days Remaining: \(status.days_remaining ?? 0)
            Status: \(status.valid ? "Valid" : status.message)

            Machine ID: \(machineID)
            """
            Dialogs.info(title: "License Information", message: message)
        } catch {
            Dialogs.error(title: "License Information", message: error.localizedDescription)
        }
    }

    func detectCameras() {
        guard !isDetectingCameras else {
            return
        }

        isDetectingCameras = true
        camerasDetected = false
        cameraStatusText = "Detecting cameras..."
        cameraStatusKind = .info

        let service = cameraService
        Task.detached(priority: .userInitiated) { [weak self] in
            do {
                let cameras = try service.detect(maxCameras: 10)
                await MainActor.run {
                    self?.handleCameraDetectionSuccess(cameras)
                }
            } catch {
                let message = error.localizedDescription
                await MainActor.run {
                    self?.handleCameraDetectionFailure(message)
                }
            }
        }
    }

    func handleSourceSelectionChanged() {
        if suppressNextSourceChange {
            suppressNextSourceChange = false
            return
        }

        if selectedSourceOption == "Video File (Browse)" {
            browseVideoSource()
            return
        }

        if let cameraIndex = parseCameraIndex(from: selectedSourceOption) {
            config.source = .int(cameraIndex)
            camerasDetected = true
        } else if !selectedSourceOption.isEmpty {
            config.source = .string(selectedSourceOption)
            camerasDetected = true
        }
    }

    func browseVideoSource() {
        let panel = NSOpenPanel()
        panel.title = "Select Video File"
        panel.allowedContentTypes = [
            UTType(filenameExtension: "mp4"),
            UTType(filenameExtension: "avi"),
            UTType(filenameExtension: "mov"),
            UTType(filenameExtension: "mkv")
        ].compactMap { $0 }
        panel.allowsMultipleSelection = false
        panel.canChooseDirectories = false

        guard panel.runModal() == .OK, let url = panel.url else {
            return
        }

        let option = "File: \(url.path)"
        sourceOptions.removeAll { $0.hasPrefix("File:") }
        insertFileOption(option)
        setSourceSelection(option)
        config.source = .string(url.path)
        cameraStatusText = "Video file selected"
        cameraStatusKind = .success
        camerasDetected = true
    }

    func browseModelPath() {
        let panel = NSOpenPanel()
        panel.title = "Select YOLO Model"
        panel.allowedContentTypes = [UTType(filenameExtension: "pt")].compactMap { $0 }
        panel.allowsMultipleSelection = false
        panel.canChooseDirectories = false

        guard panel.runModal() == .OK, let url = panel.url else {
            return
        }
        config.model_path = url.path
    }

    func loadConfigFile() {
        let panel = NSOpenPanel()
        panel.title = "Load Configuration"
        panel.allowedContentTypes = [.json]
        panel.allowsMultipleSelection = false
        panel.canChooseDirectories = false

        guard panel.runModal() == .OK, let url = panel.url else {
            return
        }

        do {
            try loadConfig(from: url)
            statusText = "Configuration loaded from \(url.path)"
            Dialogs.info(title: "Success", message: "Configuration loaded successfully from:\n\(url.path)")
        } catch {
            Dialogs.error(title: "Error", message: "Failed to load configuration:\n\(error.localizedDescription)")
        }
    }

    func saveConfigFile() {
        let panel = NSSavePanel()
        panel.title = "Save Configuration"
        panel.allowedContentTypes = [.json]
        panel.nameFieldStringValue = "system_conf.json"

        guard panel.runModal() == .OK, let url = panel.url else {
            return
        }

        do {
            let currentConfig = collectConfigFromUI()
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            let data = try encoder.encode(currentConfig)
            try data.write(to: url)
            statusText = "Configuration saved to \(url.path)"
            Dialogs.info(title: "Success", message: "Configuration saved successfully to:\n\(url.path)")
        } catch {
            Dialogs.error(title: "Error", message: "Failed to save configuration:\n\(error.localizedDescription)")
        }
    }

    func resetToDefaults() {
        guard Dialogs.confirm(title: "Confirm Reset", message: "Reset all settings to default values?") else {
            return
        }
        config = MonitoringConfig()
        selectSourceFromConfig(preferFirstCamera: true)
        statusText = "Configuration reset to defaults"
    }

    func runMonitor() {
        if monitorIsRunning {
            Dialogs.warning(title: "Monitor Running", message: "The monitoring system is already running.")
            return
        }

        guard camerasDetected else {
            Dialogs.warning(
                title: "No Video Source",
                message: "Please wait for camera detection to complete or select a video file."
            )
            return
        }

        do {
            let status = try licenseService.status()
            updateLicenseStatus(status)
            guard status.valid else {
                Dialogs.error(title: "License Error", message: "Cannot run: \(status.message)")
                return
            }
            try python.requireOpenCV()

            let runConfig = collectConfigFromUI()
            let configURL = try writeMonitorConfig(runConfig)
            let process = Process()
            process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
            process.arguments = [python.command, paths.mainScript.path, "--config-file", configURL.path]
            process.currentDirectoryURL = paths.appDirectory
            process.terminationHandler = { [weak self] process in
                let pid = process.processIdentifier
                let status = process.terminationStatus
                Task { @MainActor [weak self] in
                    self?.monitorProcessEnded(pid: pid, status: status)
                }
            }

            try process.run()
            monitorProcess = process
            monitorPID = process.processIdentifier
            monitorConfigURL = configURL
            stopRequested = false
            monitorIsRunning = true
            statusText = "Monitoring system running..."
        } catch {
            cleanupMonitorConfig()
            monitorProcess = nil
            monitorPID = nil
            monitorIsRunning = false
            Dialogs.error(title: "Error", message: "Failed to start monitoring system:\n\(error.localizedDescription)")
        }
    }

    func stopMonitor() {
        guard let process = monitorProcess, process.isRunning else {
            monitorEnded()
            return
        }

        stopRequested = true
        statusText = "Stopping monitoring system..."
        process.interrupt()

        DispatchQueue.main.asyncAfter(deadline: .now() + 5) { [weak self] in
            self?.terminateMonitorProcessIfNeeded()
        }
    }

    func stopMonitorForTermination() {
        stopRequested = true
        if let process = monitorProcess, process.isRunning {
            process.interrupt()
            process.terminate()
        }
        cleanupMonitorConfig()
    }

    private func finishStartup() {
        if !startupFinished {
            loadSystemConfig()
            scheduleLicenseCheck()
            startupFinished = true
        }
        detectCameras()
    }

    private func scheduleLicenseCheck() {
        licenseTimer?.invalidate()
        licenseTimer = Timer.scheduledTimer(withTimeInterval: 300, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                self?.validatePeriodicLicense()
            }
        }
    }

    private func validatePeriodicLicense() {
        do {
            let status = try licenseService.status()
            updateLicenseStatus(status)
            guard status.valid else {
                Dialogs.error(
                    title: "License Invalid",
                    message: "License validation failed: \(status.message)\n\nApplication will close."
                )
                NSApplication.shared.terminate(nil)
                return
            }
        } catch {
            Dialogs.error(title: "License Invalid", message: error.localizedDescription)
            NSApplication.shared.terminate(nil)
        }
    }

    private func loadSystemConfig() {
        guard FileManager.default.fileExists(atPath: paths.systemConfig.path) else {
            return
        }

        do {
            try loadConfig(from: paths.systemConfig)
            statusText = "Loaded configuration from system_conf.json"
        } catch {
            statusText = "Warning: Could not load system_conf.json"
        }
    }

    private func loadConfig(from url: URL) throws {
        let data = try Data(contentsOf: url)
        guard let object = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw ServiceError.invalidJSON("Configuration must be a JSON object.")
        }
        config.apply(jsonObject: object)
        selectSourceFromConfig(preferFirstCamera: false)
    }

    private func updateLicenseStatus(_ status: LicenseStatus) {
        if status.valid {
            licenseStatusText = "Licensed | \(status.days_remaining ?? 0) days remaining"
        } else {
            licenseStatusText = "License: Invalid"
        }
    }

    private func handleCameraDetectionSuccess(_ cameras: [CameraInfo]) {
        availableCameras = cameras
        isDetectingCameras = false
        rebuildSourceOptions()

        if cameras.isEmpty {
            cameraStatusText = "No cameras found. Use Browse File for video."
            cameraStatusKind = .warning
            camerasDetected = false
            if selectedSourceOption.isEmpty {
                setSourceSelection("Video File (Browse)")
            }
            return
        }

        cameraStatusText = "\(cameras.count) camera(s) detected"
        cameraStatusKind = .success
        camerasDetected = true
        selectSourceFromConfig(preferFirstCamera: true)
    }

    private func handleCameraDetectionFailure(_ message: String) {
        isDetectingCameras = false
        camerasDetected = false
        cameraStatusText = "Detection failed: \(message)"
        cameraStatusKind = .error
        rebuildSourceOptions()
        Dialogs.error(title: "Camera Detection Error", message: "Failed to detect cameras:\n\(message)")
    }

    private func rebuildSourceOptions() {
        var options = availableCameras.map(cameraOption)
        options.append("Video File (Browse)")
        if selectedSourceOption.hasPrefix("File:") {
            options.insert(selectedSourceOption, at: max(0, options.count - 1))
        }
        sourceOptions = options
    }

    private func selectSourceFromConfig(preferFirstCamera: Bool) {
        if let option = option(for: config.source) {
            setSourceSelection(option)
            camerasDetected = true
            return
        }

        if preferFirstCamera, let first = availableCameras.first {
            let option = cameraOption(first)
            config.source = .int(first.index)
            setSourceSelection(option)
            camerasDetected = true
        }
    }

    private func option(for source: SourceValue) -> String? {
        if let index = source.cameraIndex,
           let camera = availableCameras.first(where: { $0.index == index }) {
            return cameraOption(camera)
        }

        let value = source.stringValue
        guard !value.isEmpty, Int(value) == nil else {
            return nil
        }

        let option = "File: \(value)"
        insertFileOption(option)
        return option
    }

    private func insertFileOption(_ option: String) {
        if !sourceOptions.contains(option) {
            let insertIndex = sourceOptions.last == "Video File (Browse)" ? max(0, sourceOptions.count - 1) : sourceOptions.count
            sourceOptions.insert(option, at: insertIndex)
        }
    }

    private func setSourceSelection(_ option: String) {
        suppressNextSourceChange = true
        selectedSourceOption = option
    }

    private func cameraOption(_ camera: CameraInfo) -> String {
        "\(camera.index) - \(camera.name)"
    }

    private func parseCameraIndex(from option: String) -> Int? {
        guard let range = option.range(of: " - ") else {
            return nil
        }
        return Int(option[..<range.lowerBound])
    }

    private func collectConfigFromUI() -> MonitoringConfig {
        var current = config
        if selectedSourceOption.hasPrefix("File:") {
            current.source = .string(selectedSourceOption.replacingOccurrences(of: "File:", with: "").trimmingCharacters(in: .whitespaces))
        } else if let cameraIndex = parseCameraIndex(from: selectedSourceOption) {
            current.source = .int(cameraIndex)
        } else if !selectedSourceOption.isEmpty, selectedSourceOption != "Video File (Browse)" {
            current.source = .string(selectedSourceOption)
        }
        return current
    }

    private func writeMonitorConfig(_ config: MonitoringConfig) throws -> URL {
        cleanupMonitorConfig()
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("stampede-monitor-\(UUID().uuidString)")
            .appendingPathExtension("json")
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let data = try encoder.encode(config)
        try data.write(to: url)
        return url
    }

    private func monitorProcessEnded(pid: Int32, status: Int32) {
        guard monitorPID == pid else {
            return
        }

        monitorProcess = nil
        monitorPID = nil
        cleanupMonitorConfig()

        if status != 0, status != -SIGINT, !stopRequested {
            Dialogs.error(
                title: "Monitor Error",
                message: "Monitoring process exited with code \(status). Check the log for details."
            )
        }
        monitorEnded()
    }

    private func monitorEnded() {
        monitorIsRunning = false
        statusText = "Monitoring system stopped"
        stopRequested = false
    }

    private func terminateMonitorProcessIfNeeded() {
        guard let process = monitorProcess, process.isRunning else {
            return
        }
        process.terminate()
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) { [weak self] in
            self?.killMonitorProcessIfNeeded()
        }
    }

    private func killMonitorProcessIfNeeded() {
        guard let process = monitorProcess, process.isRunning else {
            return
        }
        Darwin.kill(process.processIdentifier, SIGKILL)
    }

    private func cleanupMonitorConfig() {
        guard let url = monitorConfigURL else {
            return
        }
        try? FileManager.default.removeItem(at: url)
        monitorConfigURL = nil
    }
}

enum StatusKind: Sendable {
    case info
    case success
    case warning
    case error
}
