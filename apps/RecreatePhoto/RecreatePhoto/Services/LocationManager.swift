//
//  LocationManager.swift
//  RecreatePhoto
//
//  Handles location tracking and permissions (while using app)
//

import Foundation
import CoreLocation
import Combine

class LocationManager: NSObject, ObservableObject {
    @Published var currentLocation: CLLocation?
    @Published var authorizationStatus: CLAuthorizationStatus
    @Published var isTracking = false

    private let locationManager = CLLocationManager()
    private var lastNotificationCheck: Date?
    private let notificationCooldown: TimeInterval = 3600 // 1 hour between checks

    override init() {
        self.authorizationStatus = locationManager.authorizationStatus
        super.init()

        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyNearestTenMeters
        locationManager.distanceFilter = 10 // Update every 10 meters
    }

    // MARK: - Permission Handling

    func requestLocationPermission() {
        locationManager.requestWhenInUseAuthorization()
    }

    // MARK: - Location Tracking

    func startTracking() {
        guard authorizationStatus == .authorizedWhenInUse || authorizationStatus == .authorizedAlways else {
            requestLocationPermission()
            return
        }

        locationManager.startUpdatingLocation()
        isTracking = true
    }

    func stopTracking() {
        locationManager.stopUpdatingLocation()
        isTracking = false
    }

    // MARK: - Notification Logic

    func shouldCheckForNearbyPhotos() -> Bool {
        guard let lastCheck = lastNotificationCheck else {
            return true
        }

        return Date().timeIntervalSince(lastCheck) > notificationCooldown
    }

    func markNotificationCheckPerformed() {
        lastNotificationCheck = Date()
    }
}

// MARK: - CLLocationManagerDelegate

extension LocationManager: CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        currentLocation = location
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location manager error: \(error.localizedDescription)")
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorizationStatus = manager.authorizationStatus

        // Start tracking if authorized and previously requested
        if isTracking && (authorizationStatus == .authorizedWhenInUse || authorizationStatus == .authorizedAlways) {
            locationManager.startUpdatingLocation()
        }
    }
}
