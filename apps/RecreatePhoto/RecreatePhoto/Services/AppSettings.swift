//
//  AppSettings.swift
//  RecreatePhoto
//
//  User preferences and app settings
//

import Foundation
import Combine

class AppSettings: ObservableObject {
    // Proximity settings
    @Published var proximityRadiusMeters: Double {
        didSet { UserDefaults.standard.set(proximityRadiusMeters, forKey: "proximityRadiusMeters") }
    }

    @Published var clusterRadiusMeters: Double {
        didSet { UserDefaults.standard.set(clusterRadiusMeters, forKey: "clusterRadiusMeters") }
    }

    // Filter settings
    @Published var favoritesOnly: Bool {
        didSet { UserDefaults.standard.set(favoritesOnly, forKey: "favoritesOnly") }
    }

    @Published var minimumPhotoAgeMonths: Int {
        didSet { UserDefaults.standard.set(minimumPhotoAgeMonths, forKey: "minimumPhotoAgeMonths") }
    }

    // Notification settings
    @Published var notificationsEnabled: Bool {
        didSet { UserDefaults.standard.set(notificationsEnabled, forKey: "notificationsEnabled") }
    }

    @Published var notificationCooldownHours: Int {
        didSet { UserDefaults.standard.set(notificationCooldownHours, forKey: "notificationCooldownHours") }
    }

    // Camera overlay settings
    @Published var overlayOpacity: Double {
        didSet { UserDefaults.standard.set(overlayOpacity, forKey: "overlayOpacity") }
    }

    init() {
        // Load from UserDefaults or use defaults
        self.proximityRadiusMeters = UserDefaults.standard.object(forKey: "proximityRadiusMeters") as? Double ?? 50.0
        self.clusterRadiusMeters = UserDefaults.standard.object(forKey: "clusterRadiusMeters") as? Double ?? 15.0
        self.favoritesOnly = UserDefaults.standard.bool(forKey: "favoritesOnly")
        self.minimumPhotoAgeMonths = UserDefaults.standard.object(forKey: "minimumPhotoAgeMonths") as? Int ?? 0
        self.notificationsEnabled = UserDefaults.standard.object(forKey: "notificationsEnabled") as? Bool ?? true
        self.notificationCooldownHours = UserDefaults.standard.object(forKey: "notificationCooldownHours") as? Int ?? 24
        self.overlayOpacity = UserDefaults.standard.object(forKey: "overlayOpacity") as? Double ?? 0.5
    }

    var currentFilters: PhotoFilters {
        PhotoFilters(
            favoritesOnly: favoritesOnly,
            minimumAgeMonths: minimumPhotoAgeMonths > 0 ? minimumPhotoAgeMonths : nil
        )
    }
}
