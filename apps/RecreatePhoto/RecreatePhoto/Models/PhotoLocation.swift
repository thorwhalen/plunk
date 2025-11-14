//
//  PhotoLocation.swift
//  RecreatePhoto
//
//  Core data models for photos and their locations
//

import Foundation
import CoreLocation
import Photos

/// Represents a photo with its location metadata
struct PhotoLocation: Identifiable, Codable {
    let id: String // PHAsset localIdentifier
    let latitude: Double
    let longitude: Double
    let captureDate: Date
    let albumName: String?
    let isFavorite: Bool

    // Optional EXIF metadata
    let focalLength: Double?
    let orientation: Int?

    var coordinate: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }

    var location: CLLocation {
        CLLocation(latitude: latitude, longitude: longitude)
    }

    init(asset: PHAsset) {
        self.id = asset.localIdentifier
        self.latitude = asset.location?.coordinate.latitude ?? 0
        self.longitude = asset.location?.coordinate.longitude ?? 0
        self.captureDate = asset.creationDate ?? Date()
        self.albumName = nil // Will be populated separately
        self.isFavorite = asset.isFavorite
        self.focalLength = nil // Would need to parse EXIF
        self.orientation = nil
    }

    init(id: String, latitude: Double, longitude: Double, captureDate: Date,
         albumName: String?, isFavorite: Bool, focalLength: Double?, orientation: Int?) {
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.captureDate = captureDate
        self.albumName = albumName
        self.isFavorite = isFavorite
        self.focalLength = focalLength
        self.orientation = orientation
    }
}

/// Represents a cluster of photos taken at similar locations
struct PhotoSpot: Identifiable {
    let id = UUID()
    let centerCoordinate: CLLocationCoordinate2D
    let photos: [PhotoLocation]
    let radius: Double // meters

    var representativePhoto: PhotoLocation? {
        photos.first
    }

    var photoCount: Int {
        photos.count
    }

    var dateRange: String {
        guard let oldest = photos.map({ $0.captureDate }).min(),
              let newest = photos.map({ $0.captureDate }).max() else {
            return ""
        }

        let formatter = DateFormatter()
        formatter.dateStyle = .medium

        if Calendar.current.isDate(oldest, inSameDayAs: newest) {
            return formatter.string(from: oldest)
        } else {
            return "\(formatter.string(from: oldest)) - \(formatter.string(from: newest))"
        }
    }
}

/// Persistent cache for photo index
struct PhotoIndexCache: Codable {
    let photos: [PhotoLocation]
    let lastUpdated: Date
    let version: Int

    static let currentVersion = 1
}
