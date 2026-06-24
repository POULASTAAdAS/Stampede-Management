import AppKit
import SwiftUI

@main
struct StampedeConfigSwiftApp: App {
    @StateObject private var viewModel = ConfigurationViewModel()
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate

    var body: some Scene {
        WindowGroup("Crowd Monitoring System - Configuration Manager") {
            ContentView(viewModel: viewModel)
                .frame(minWidth: 760, minHeight: 520)
                .onAppear {
                    appDelegate.viewModel = viewModel
                    viewModel.startIfNeeded()
                }
        }
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
    }
}

@MainActor
final class AppDelegate: NSObject, NSApplicationDelegate {
    weak var viewModel: ConfigurationViewModel?

    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        guard let viewModel, viewModel.monitorIsRunning else {
            return .terminateNow
        }

        let shouldExit = Dialogs.confirm(
            title: "Exit",
            message: "Monitoring is still running. Close the configuration UI and leave it running?\n\nUse Stop Monitor before exiting if you want to close the room."
        )
        if shouldExit {
            return .terminateNow
        }
        return .terminateCancel
    }
}
