//
//  ContentView.swift
//  RecreatePhoto
//
//  Main tab-based navigation
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var photoIndexer: PhotoIndexer
    @EnvironmentObject var locationManager: LocationManager
    @EnvironmentObject var appSettings: AppSettings

    var body: some View {
        TabView {
            NearbyPhotosView()
                .tabItem {
                    Label("Nearby", systemImage: "location.circle.fill")
                }

            MapView()
                .tabItem {
                    Label("Map", systemImage: "map.fill")
                }

            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gearshape.fill")
                }
        }
        .onAppear {
            // Start location tracking when app appears
            locationManager.startTracking()
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(PhotoIndexer())
        .environmentObject(LocationManager())
        .environmentObject(AppSettings())
}
