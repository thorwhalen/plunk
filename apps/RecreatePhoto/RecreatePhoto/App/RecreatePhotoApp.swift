//
//  RecreatePhotoApp.swift
//  RecreatePhoto
//
//  Main application entry point
//

import SwiftUI

@main
struct RecreatePhotoApp: App {
    @StateObject private var photoIndexer = PhotoIndexer()
    @StateObject private var locationManager = LocationManager()
    @StateObject private var appSettings = AppSettings()
    @StateObject private var notificationManager = NotificationManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(photoIndexer)
                .environmentObject(locationManager)
                .environmentObject(appSettings)
                .environmentObject(notificationManager)
                .onAppear {
                    // Request permissions on first launch
                    photoIndexer.requestPhotoLibraryAccess()
                    notificationManager.requestAuthorization()
                }
        }
    }
}
