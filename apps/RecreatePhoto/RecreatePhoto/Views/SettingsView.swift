//
//  SettingsView.swift
//  RecreatePhoto
//
//  User preferences and settings
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var photoIndexer: PhotoIndexer
    @EnvironmentObject var locationManager: LocationManager
    @EnvironmentObject var appSettings: AppSettings

    var body: some View {
        NavigationView {
            Form {
                // Photo Library Section
                Section {
                    HStack {
                        Text("Indexed Photos")
                        Spacer()
                        Text("\(photoIndexer.indexedPhotos.count)")
                            .foregroundColor(.secondary)
                    }

                    Button("Reindex Photo Library") {
                        photoIndexer.indexPhotoLibrary(forceReindex: true)
                    }
                    .disabled(photoIndexer.isIndexing)

                    if photoIndexer.isIndexing {
                        ProgressView(value: photoIndexer.indexProgress)
                    }
                } header: {
                    Text("Photo Library")
                }

                // Location Section
                Section {
                    HStack {
                        Text("Location Access")
                        Spacer()
                        Text(locationStatusText)
                            .foregroundColor(.secondary)
                    }

                    if locationManager.authorizationStatus != .authorizedWhenInUse &&
                       locationManager.authorizationStatus != .authorizedAlways {
                        Button("Request Location Access") {
                            locationManager.requestLocationPermission()
                        }
                    }

                    Toggle("Track Location", isOn: Binding(
                        get: { locationManager.isTracking },
                        set: { isOn in
                            if isOn {
                                locationManager.startTracking()
                            } else {
                                locationManager.stopTracking()
                            }
                        }
                    ))
                } header: {
                    Text("Location")
                } footer: {
                    Text("Location is only tracked while the app is in use.")
                }

                // Proximity Settings
                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Proximity Radius: \(Int(appSettings.proximityRadiusMeters))m")
                        Slider(value: $appSettings.proximityRadiusMeters, in: 20...200, step: 10)
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Text("Cluster Radius: \(Int(appSettings.clusterRadiusMeters))m")
                        Slider(value: $appSettings.clusterRadiusMeters, in: 5...50, step: 5)
                    }
                } header: {
                    Text("Proximity Settings")
                } footer: {
                    Text("Proximity radius determines how close you need to be to a photo location. Cluster radius groups nearby photos together.")
                }

                // Filter Settings
                Section {
                    Toggle("Favorites Only", isOn: $appSettings.favoritesOnly)

                    Picker("Minimum Photo Age", selection: $appSettings.minimumPhotoAgeMonths) {
                        Text("All Photos").tag(0)
                        Text("3 Months").tag(3)
                        Text("6 Months").tag(6)
                        Text("1 Year").tag(12)
                        Text("2 Years").tag(24)
                    }
                } header: {
                    Text("Photo Filters")
                } footer: {
                    Text("Only show photos matching these criteria.")
                }

                // Camera Settings
                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Overlay Opacity: \(Int(appSettings.overlayOpacity * 100))%")
                        Slider(value: $appSettings.overlayOpacity, in: 0.1...0.9, step: 0.1)
                    }
                } header: {
                    Text("Camera Overlay")
                } footer: {
                    Text("Default opacity for the photo overlay in recreate mode.")
                }

                // Notifications Section
                Section {
                    Toggle("Enable Notifications", isOn: $appSettings.notificationsEnabled)

                    Picker("Cooldown Period", selection: $appSettings.notificationCooldownHours) {
                        Text("1 Hour").tag(1)
                        Text("6 Hours").tag(6)
                        Text("24 Hours").tag(24)
                        Text("1 Week").tag(168)
                    }
                    .disabled(!appSettings.notificationsEnabled)
                } header: {
                    Text("Notifications")
                } footer: {
                    Text("Minimum time between notifications for the same location.")
                }

                // About Section
                Section {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }
                } header: {
                    Text("About")
                }
            }
            .navigationTitle("Settings")
        }
    }

    private var locationStatusText: String {
        switch locationManager.authorizationStatus {
        case .notDetermined:
            return "Not Requested"
        case .restricted:
            return "Restricted"
        case .denied:
            return "Denied"
        case .authorizedAlways:
            return "Always"
        case .authorizedWhenInUse:
            return "While Using"
        @unknown default:
            return "Unknown"
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(PhotoIndexer())
        .environmentObject(LocationManager())
        .environmentObject(AppSettings())
}
