//
//  NearbyPhotosView.swift
//  RecreatePhoto
//
//  Shows photos near the user's current location
//

import SwiftUI
import CoreLocation

struct NearbyPhotosView: View {
    @EnvironmentObject var photoIndexer: PhotoIndexer
    @EnvironmentObject var locationManager: LocationManager
    @EnvironmentObject var appSettings: AppSettings
    @EnvironmentObject var notificationManager: NotificationManager

    @State private var nearbySpots: [PhotoSpot] = []
    @State private var selectedSpot: PhotoSpot?
    @State private var showingPermissionAlert = false

    var body: some View {
        NavigationView {
            VStack {
                if photoIndexer.authorizationStatus != .authorized && photoIndexer.authorizationStatus != .limited {
                    photoLibraryPermissionView
                } else if locationManager.authorizationStatus != .authorizedWhenInUse && locationManager.authorizationStatus != .authorizedAlways {
                    locationPermissionView
                } else if photoIndexer.isIndexing {
                    indexingView
                } else if nearbySpots.isEmpty {
                    emptyStateView
                } else {
                    spotsList
                }
            }
            .navigationTitle("Nearby Photos")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: refreshNearbyPhotos) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .onAppear {
                refreshNearbyPhotos()
            }
            .onChange(of: locationManager.currentLocation) { _ in
                refreshNearbyPhotos()
            }
        }
    }

    // MARK: - Subviews

    private var photoLibraryPermissionView: some View {
        VStack(spacing: 20) {
            Image(systemName: "photo.on.rectangle.angled")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text("Photo Library Access Required")
                .font(.headline)

            Text("RecreatePhoto needs access to your photos to find locations where you've taken pictures.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)

            Button("Grant Access") {
                photoIndexer.requestPhotoLibraryAccess()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }

    private var locationPermissionView: some View {
        VStack(spacing: 20) {
            Image(systemName: "location.circle")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text("Location Access Required")
                .font(.headline)

            Text("RecreatePhoto needs your location to find photos taken nearby.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)

            Button("Grant Access") {
                locationManager.requestLocationPermission()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }

    private var indexingView: some View {
        VStack(spacing: 20) {
            ProgressView(value: photoIndexer.indexProgress) {
                Text("Indexing your photos...")
            }
            .padding()

            Text("\(Int(photoIndexer.indexProgress * 100))%")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
    }

    private var emptyStateView: some View {
        VStack(spacing: 20) {
            Image(systemName: "photo.on.rectangle")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text("No Photos Nearby")
                .font(.headline)

            if let location = locationManager.currentLocation {
                Text("No geotagged photos found within \(Int(appSettings.proximityRadiusMeters))m of your current location.")
                    .multilineTextAlignment(.center)
                    .foregroundColor(.secondary)
                    .padding(.horizontal)
            } else {
                Text("Waiting for location...")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
    }

    private var spotsList: some View {
        List(nearbySpots) { spot in
            NavigationLink(destination: SpotDetailView(spot: spot)) {
                SpotRowView(spot: spot)
            }
        }
    }

    // MARK: - Actions

    private func refreshNearbyPhotos() {
        guard let location = locationManager.currentLocation else {
            return
        }

        nearbySpots = photoIndexer.getSpotsNear(
            location: location,
            radius: appSettings.proximityRadiusMeters,
            clusterRadius: appSettings.clusterRadiusMeters,
            filters: appSettings.currentFilters
        )

        // Check if we should send notification
        if !nearbySpots.isEmpty && locationManager.shouldCheckForNearbyPhotos() {
            notificationManager.checkAndNotifyForNearbyPhotos(
                spots: nearbySpots,
                location: location,
                settings: appSettings
            )
            locationManager.markNotificationCheckPerformed()
        }
    }
}

// MARK: - Supporting Views

struct SpotRowView: View {
    let spot: PhotoSpot

    var body: some View {
        HStack {
            if let firstPhoto = spot.representativePhoto,
               let asset = PhotoIndexer().getAsset(for: firstPhoto) {
                ThumbnailView(asset: asset)
                    .frame(width: 60, height: 60)
                    .cornerRadius(8)
            }

            VStack(alignment: .leading, spacing: 4) {
                Text("\(spot.photoCount) photo\(spot.photoCount == 1 ? "" : "s")")
                    .font(.headline)

                Text(spot.dateRange)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    NearbyPhotosView()
        .environmentObject(PhotoIndexer())
        .environmentObject(LocationManager())
        .environmentObject(AppSettings())
        .environmentObject(NotificationManager())
}
