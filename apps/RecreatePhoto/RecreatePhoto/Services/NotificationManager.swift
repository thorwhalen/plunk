//
//  NotificationManager.swift
//  RecreatePhoto
//
//  Manages local notifications for nearby photo alerts
//

import Foundation
import UserNotifications
import CoreLocation

class NotificationManager: NSObject, ObservableObject {
    @Published var authorizationStatus: UNAuthorizationStatus = .notDetermined

    private let notificationCenter = UNUserNotificationCenter.current()
    private var notificationHistory: [String: Date] = [:]

    override init() {
        super.init()
        notificationCenter.delegate = self
        checkAuthorizationStatus()
    }

    // MARK: - Permission Handling

    func requestAuthorization() {
        notificationCenter.requestAuthorization(options: [.alert, .sound, .badge]) { [weak self] granted, error in
            DispatchQueue.main.async {
                self?.checkAuthorizationStatus()
            }
        }
    }

    private func checkAuthorizationStatus() {
        notificationCenter.getNotificationSettings { [weak self] settings in
            DispatchQueue.main.async {
                self?.authorizationStatus = settings.authorizationStatus
            }
        }
    }

    // MARK: - Notification Scheduling

    func scheduleNearbyPhotoNotification(spots: [PhotoSpot], location: CLLocation, cooldownHours: Int) {
        guard authorizationStatus == .authorized else {
            return
        }

        // Filter out spots we've recently notified about
        let spotsToNotify = spots.filter { spot in
            shouldNotifyForSpot(spot, cooldownHours: cooldownHours)
        }

        guard !spotsToNotify.isEmpty else {
            return
        }

        // Take the closest spot
        let sortedSpots = spotsToNotify.sorted { spot1, spot2 in
            let dist1 = location.distance(from: CLLocation(
                latitude: spot1.centerCoordinate.latitude,
                longitude: spot1.centerCoordinate.longitude
            ))
            let dist2 = location.distance(from: CLLocation(
                latitude: spot2.centerCoordinate.latitude,
                longitude: spot2.centerCoordinate.longitude
            ))
            return dist1 < dist2
        }

        guard let closestSpot = sortedSpots.first else {
            return
        }

        // Create notification content
        let content = UNMutableNotificationContent()
        content.title = "Photos Nearby"

        if closestSpot.photoCount == 1 {
            content.body = "You took a photo here on \(closestSpot.dateRange)"
        } else {
            content.body = "You took \(closestSpot.photoCount) photos here. \(closestSpot.dateRange)"
        }

        content.sound = .default
        content.categoryIdentifier = "NEARBY_PHOTOS"

        // Add user info for handling tap
        content.userInfo = [
            "spotLat": closestSpot.centerCoordinate.latitude,
            "spotLon": closestSpot.centerCoordinate.longitude,
            "photoCount": closestSpot.photoCount
        ]

        // Schedule immediately
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: nil // Deliver immediately
        )

        notificationCenter.add(request) { error in
            if let error = error {
                print("Error scheduling notification: \(error)")
            } else {
                // Mark this spot as notified
                self.markSpotNotified(closestSpot)
            }
        }
    }

    // MARK: - Notification History

    private func shouldNotifyForSpot(_ spot: PhotoSpot, cooldownHours: Int) -> Bool {
        let spotKey = "\(spot.centerCoordinate.latitude),\(spot.centerCoordinate.longitude)"

        guard let lastNotification = notificationHistory[spotKey] else {
            return true
        }

        let cooldownSeconds = TimeInterval(cooldownHours * 3600)
        return Date().timeIntervalSince(lastNotification) > cooldownSeconds
    }

    private func markSpotNotified(_ spot: PhotoSpot) {
        let spotKey = "\(spot.centerCoordinate.latitude),\(spot.centerCoordinate.longitude)"
        notificationHistory[spotKey] = Date()

        // Save to UserDefaults
        if let data = try? JSONEncoder().encode(notificationHistory) {
            UserDefaults.standard.set(data, forKey: "notificationHistory")
        }
    }

    private func loadNotificationHistory() {
        guard let data = UserDefaults.standard.data(forKey: "notificationHistory"),
              let history = try? JSONDecoder().decode([String: Date].self, from: data) else {
            return
        }
        notificationHistory = history
    }

    // MARK: - Public Methods

    func checkAndNotifyForNearbyPhotos(spots: [PhotoSpot], location: CLLocation, settings: AppSettings) {
        guard settings.notificationsEnabled else {
            return
        }

        scheduleNearbyPhotoNotification(
            spots: spots,
            location: location,
            cooldownHours: settings.notificationCooldownHours
        )
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationManager: UNUserNotificationCenterDelegate {
    // Handle notification when app is in foreground
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound])
    }

    // Handle notification tap
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        // Could navigate to specific spot based on userInfo
        // For now, just complete
        completionHandler()
    }
}
