// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "StampedeConfigSwift",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "StampedeConfigSwift",
            targets: ["StampedeConfigSwift"]
        )
    ],
    targets: [
        .executableTarget(name: "StampedeConfigSwift")
    ]
)
