import SwiftUI

struct ContentView: View {
    @ObservedObject var viewModel: ConfigurationViewModel

    var body: some View {
        VStack(spacing: 10) {
            TabView {
                VideoSourceTab(viewModel: viewModel)
                    .tabItem { Text("Video Source") }
                GridSpatialTab(viewModel: viewModel)
                    .tabItem { Text("Grid & Spatial") }
                DetectionTab(viewModel: viewModel)
                    .tabItem { Text("Detection") }
                TrackingTab(viewModel: viewModel)
                    .tabItem { Text("Tracking") }
                SmoothingAlertsTab(viewModel: viewModel)
                    .tabItem { Text("Smoothing & Alerts") }
                VisualizationTab(viewModel: viewModel)
                    .tabItem { Text("Visualization") }
                InteractiveTab(viewModel: viewModel)
                    .tabItem { Text("Interactive") }
                CalibrationTab(viewModel: viewModel)
                    .tabItem { Text("Calibration") }
            }

            Divider()

            HStack(spacing: 8) {
                Button("Load Config") { viewModel.loadConfigFile() }
                Button("Save Config") { viewModel.saveConfigFile() }
                Button("Reset to Defaults") { viewModel.resetToDefaults() }
                Button("License Info") { viewModel.showLicenseInfo() }
                Spacer()
                Button("Stop Monitor") { viewModel.stopMonitor() }
                    .disabled(!viewModel.monitorIsRunning)
                Button("Run Monitor") { viewModel.runMonitor() }
                    .keyboardShortcut(.defaultAction)
                    .disabled(!viewModel.canRunMonitor)
            }

            HStack(spacing: 8) {
                Text(viewModel.statusText)
                    .lineLimit(1)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.secondary.opacity(0.12))
                    .clipShape(RoundedRectangle(cornerRadius: 4))

                Text(viewModel.licenseStatusText)
                    .lineLimit(1)
                    .frame(width: 230, alignment: .trailing)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.secondary.opacity(0.12))
                    .clipShape(RoundedRectangle(cornerRadius: 4))
            }
        }
        .padding(10)
        .sheet(isPresented: $viewModel.showActivation) {
            ActivationView(viewModel: viewModel)
                .frame(width: 620, height: 720)
                .interactiveDismissDisabled(true)
        }
    }
}

struct ActivationView: View {
    @ObservedObject var viewModel: ConfigurationViewModel
    @State private var licenseText = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            VStack(alignment: .leading, spacing: 6) {
                Text("License Activation Required")
                    .font(.title2.bold())
                Text("Please enter your license key to activate the application.")
                    .foregroundStyle(.secondary)
            }

            GroupBox("Your Machine Information") {
                VStack(alignment: .leading, spacing: 8) {
                    MonospaceLine(label: "MAC Address", value: viewModel.activationMachineInfo.macAddress)
                    MonospaceLine(label: "Username", value: viewModel.activationMachineInfo.username)
                    MonospaceLine(label: "Machine ID", value: viewModel.activationMachineInfo.machineID)
                    Text("Send all three values above to support to request a license.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .padding(.top, 6)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(4)
            }

            GroupBox("License Key") {
                TextEditor(text: $licenseText)
                    .font(.system(.body, design: .monospaced))
                    .frame(minHeight: 220)
            }

            VStack(spacing: 8) {
                HStack {
                    Button("Copy Machine Info") { viewModel.copyMachineInfo() }
                    Button("Activate License") { viewModel.activateLicense(licenseText) }
                        .keyboardShortcut(.defaultAction)
                }
                HStack {
                    Button("License Info") { viewModel.showLicenseInfo() }
                    Button("Exit") { viewModel.handleActivationExit() }
                }
            }
            .frame(maxWidth: .infinity)

            Text("Need help? Contact support.")
                .font(.caption)
                .foregroundStyle(.secondary)
                .frame(maxWidth: .infinity, alignment: .center)
        }
        .padding(20)
    }
}

struct MonospaceLine: View {
    var label: String
    var value: String

    var body: some View {
        Text("\(label): \(value)")
            .font(.system(.callout, design: .monospaced))
            .textSelection(.enabled)
    }
}

struct VideoSourceTab: View {
    @ObservedObject var viewModel: ConfigurationViewModel

    var body: some View {
        SettingsScrollView {
            SettingsSection(title: "Video Source Settings") {
                SettingRow(title: "Video Source") {
                    Picker("", selection: $viewModel.selectedSourceOption) {
                        ForEach(viewModel.sourceOptions, id: \.self) { option in
                            Text(option).tag(option)
                        }
                    }
                    .labelsHidden()
                    .frame(width: 300)
                    .disabled(viewModel.isDetectingCameras)
                    .onChange(of: viewModel.selectedSourceOption) { _ in
                        viewModel.handleSourceSelectionChanged()
                    }

                    Button("Detect Cameras") { viewModel.detectCameras() }
                        .disabled(viewModel.isDetectingCameras)
                    Button("Browse File") { viewModel.browseVideoSource() }
                    StatusText(text: viewModel.cameraStatusText, kind: viewModel.cameraStatusKind)
                }

                SettingRow(title: "Model Path") {
                    TextField("Model path", text: $viewModel.config.model_path)
                        .frame(width: 300)
                    Button("Browse") { viewModel.browseModelPath() }
                    HelpText("Path to YOLO model file")
                }
            }

            SettingsSection(title: "Camera Settings") {
                IntSettingRow(title: "Camera Width", value: $viewModel.config.camera_width, range: 320...3840, unit: "pixels")
                IntSettingRow(title: "Camera Height", value: $viewModel.config.camera_height, range: 240...2160, unit: "pixels")
                IntSettingRow(title: "Camera FPS", value: $viewModel.config.camera_fps, range: 1...120, unit: "frames per second")
            }
        }
    }
}

struct GridSpatialTab: View {
    @ObservedObject var viewModel: ConfigurationViewModel

    var body: some View {
        SettingsScrollView {
            SettingsSection(title: "Grid Settings") {
                DoubleSettingRow(title: "Cell Width", value: $viewModel.config.cell_width, range: 0.1...10.0, step: 0.1, unit: "meters")
                DoubleSettingRow(title: "Cell Height", value: $viewModel.config.cell_height, range: 0.1...10.0, step: 0.1, unit: "meters")
                DoubleSettingRow(title: "Person Radius", value: $viewModel.config.person_radius, range: 0.1...10.0, step: 0.1, unit: "meters (for capacity calculation)")
            }
        }
    }
}

struct DetectionTab: View {
    @ObservedObject var viewModel: ConfigurationViewModel
    private let yoloSizes = [320, 416, 512, 640, 800, 1024]

    var body: some View {
        SettingsScrollView {
            SettingsSection(title: "Detection Settings") {
                IntSettingRow(title: "Detect Every N Frames", value: $viewModel.config.detect_every, range: 1...30, unit: "Higher = faster, less accurate")
                SliderSettingRow(title: "Confidence Threshold", value: $viewModel.config.confidence_threshold, range: 0.0...1.0)
                IntSettingRow(title: "Min BBox Area", value: $viewModel.config.min_bbox_area, range: 100...10000, step: 100, unit: "pixels (filter small detections)")
            }

            SettingsSection(title: "YOLO Model Settings") {
                SettingRow(title: "YOLO Image Size") {
                    Picker("", selection: $viewModel.config.yolo_imgsz) {
                        ForEach(yoloSizes, id: \.self) { size in
                            Text("\(size)").tag(size)
                        }
                    }
                    .labelsHidden()
                    .frame(width: 120)
                    HelpText("pixels (higher = slower, more accurate)")
                }
            }
        }
    }
}

struct TrackingTab: View {
    @ObservedObject var viewModel: ConfigurationViewModel

    var body: some View {
        SettingsScrollView {
            SettingsSection(title: "Tracking Settings") {
                SettingRow(title: "") {
                    Toggle("Use DeepSort Tracker", isOn: $viewModel.config.use_deepsort)
                    HelpText("Requires DeepSort library")
                }
                IntSettingRow(title: "Max Age", value: $viewModel.config.max_age, range: 1...300, unit: "frames to keep track without detection")
                IntSettingRow(title: "N Init", value: $viewModel.config.n_init, range: 1...10, unit: "frames to confirm new track")
            }

            SettingsSection(title: "Centroid Tracker Settings") {
                DoubleSettingRow(title: "Distance Threshold", value: $viewModel.config.centroid_distance_threshold, range: 10.0...500.0, step: 10.0, unit: "pixels (max distance for same person)")
            }
        }
    }
}

struct SmoothingAlertsTab: View {
    @ObservedObject var viewModel: ConfigurationViewModel

    var body: some View {
        SettingsScrollView {
            SettingsSection(title: "Smoothing Settings") {
                SliderSettingRow(title: "EMA Alpha", value: $viewModel.config.ema_alpha, range: 0.0...1.0)
                DoubleSettingRow(title: "Expected FPS", value: $viewModel.config.fps, range: 1.0...120.0, step: 1.0, unit: "for timing calculations")
                DoubleSettingRow(title: "Hysteresis Time", value: $viewModel.config.hysteresis_time, range: 0.1...10.0, step: 0.1, unit: "seconds (alert debounce time)")
            }

            SettingsSection(title: "Alert Thresholds") {
                SliderSettingRow(title: "Alert Clear Offset", value: $viewModel.config.alert_clear_offset, range: 0.0...1.0)
                SliderSettingRow(title: "Warning Threshold", value: $viewModel.config.occupancy_warning_threshold, range: 0.0...1.0)
            }
        }
    }
}

struct VisualizationTab: View {
    @ObservedObject var viewModel: ConfigurationViewModel

    var body: some View {
        SettingsScrollView {
            SettingsSection(title: "Display Settings") {
                IntSettingRow(title: "Max Bird's Eye Pixels", value: $viewModel.config.max_birdseye_pixels, range: 300...2000, step: 50, unit: "pixels")
                IntSettingRow(title: "Grid Line Thickness", value: $viewModel.config.grid_line_thickness, range: 1...10, unit: "pixels")
                IntSettingRow(title: "BBox Thickness", value: $viewModel.config.bbox_thickness, range: 1...10, unit: "pixels")
                IntSettingRow(title: "Info Panel Height", value: $viewModel.config.info_panel_height, range: 50...300, step: 10, unit: "pixels")
            }

            SettingsSection(title: "Font Sizes") {
                DoubleSettingRow(title: "Large Font", value: $viewModel.config.font_size_large, range: 0.1...2.0, step: 0.05, unit: "scale")
                DoubleSettingRow(title: "Medium Font", value: $viewModel.config.font_size_medium, range: 0.1...2.0, step: 0.05, unit: "scale")
                DoubleSettingRow(title: "Small Font", value: $viewModel.config.font_size_small, range: 0.1...2.0, step: 0.05, unit: "scale")
                DoubleSettingRow(title: "Tiny Font", value: $viewModel.config.font_size_tiny, range: 0.1...2.0, step: 0.05, unit: "scale")
                DoubleSettingRow(title: "Bird's Eye Font", value: $viewModel.config.font_size_birdseye, range: 0.1...2.0, step: 0.05, unit: "scale")
            }
        }
    }
}

struct InteractiveTab: View {
    @ObservedObject var viewModel: ConfigurationViewModel

    var body: some View {
        SettingsScrollView {
            SettingsSection(title: "Interactive Features") {
                SettingRow(title: "") {
                    Toggle("Enable Screenshots (press 's')", isOn: $viewModel.config.enable_screenshots)
                }
                SettingRow(title: "") {
                    Toggle("Enable Grid Adjustment (press 'g')", isOn: $viewModel.config.enable_grid_adjustment)
                }
            }

            SettingsSection(title: "Display Options") {
                IntSettingRow(title: "FPS Counter Window", value: $viewModel.config.fps_counter_window, range: 10...120, unit: "frames to average")
                IntSettingRow(title: "Split View Divisor", value: $viewModel.config.split_view_divisor, range: 2...4, unit: "(2 = half size, 3 = third size)")
            }
        }
    }
}

struct CalibrationTab: View {
    @ObservedObject var viewModel: ConfigurationViewModel

    var body: some View {
        SettingsScrollView {
            SettingsSection(title: "Calibration Area Dimensions") {
                Text("Set the real-world dimensions of the calibrated area")
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.leading, 10)
                DoubleSettingRow(title: "Area Width", value: $viewModel.config.calibration_area_width, range: 1.0...100.0, step: 0.5, unit: "meters (horizontal)")
                DoubleSettingRow(title: "Area Height", value: $viewModel.config.calibration_area_height, range: 1.0...100.0, step: 0.5, unit: "meters (vertical)")
                SettingRow(title: "") {
                    Toggle("Use preset dimensions (skip manual input during calibration)", isOn: $viewModel.config.auto_calibration)
                }
            }

            SettingsSection(title: "Calibration Display Settings") {
                IntSettingRow(title: "Point Radius", value: $viewModel.config.calibration_point_radius, range: 3...20, unit: "pixels")
                IntSettingRow(title: "Line Thickness", value: $viewModel.config.calibration_line_thickness, range: 1...10, unit: "pixels")
            }
        }
    }
}

struct SettingsScrollView<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                content
            }
            .padding(.vertical, 12)
            .padding(.horizontal, 10)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

struct SettingsSection<Content: View>: View {
    var title: String
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title)
                .font(.headline)
            VStack(alignment: .leading, spacing: 8) {
                content
            }
            .padding(.leading, 8)
        }
    }
}

struct SettingRow<Content: View>: View {
    var title: String
    @ViewBuilder var content: Content

    var body: some View {
        HStack(alignment: .center, spacing: 10) {
            Text(title)
                .frame(width: 170, alignment: .leading)
            content
            Spacer(minLength: 0)
        }
        .frame(minHeight: 28)
    }
}

struct IntSettingRow: View {
    var title: String
    @Binding var value: Int
    var range: ClosedRange<Int>
    var step: Int = 1
    var unit: String

    var body: some View {
        SettingRow(title: title) {
            Stepper(value: $value, in: range, step: step) {
                TextField("", value: $value, format: .number)
                    .frame(width: 80)
            }
            HelpText(unit)
        }
    }
}

struct DoubleSettingRow: View {
    var title: String
    @Binding var value: Double
    var range: ClosedRange<Double>
    var step: Double
    var unit: String

    var body: some View {
        SettingRow(title: title) {
            Stepper(value: $value, in: range, step: step) {
                TextField("", value: $value, format: .number.precision(.fractionLength(0...2)))
                    .frame(width: 80)
            }
            HelpText(unit)
        }
    }
}

struct SliderSettingRow: View {
    var title: String
    @Binding var value: Double
    var range: ClosedRange<Double>

    var body: some View {
        SettingRow(title: title) {
            Slider(value: $value, in: range)
                .frame(width: 220)
            Text(value, format: .number.precision(.fractionLength(2)))
                .frame(width: 48, alignment: .leading)
        }
    }
}

struct HelpText: View {
    var text: String

    init(_ text: String) {
        self.text = text
    }

    var body: some View {
        Text(text)
            .foregroundStyle(.secondary)
    }
}

struct StatusText: View {
    var text: String
    var kind: StatusKind

    var body: some View {
        Text(text)
            .foregroundStyle(color)
            .lineLimit(2)
    }

    private var color: Color {
        switch kind {
        case .info:
            return .blue
        case .success:
            return .green
        case .warning:
            return .orange
        case .error:
            return .red
        }
    }
}
