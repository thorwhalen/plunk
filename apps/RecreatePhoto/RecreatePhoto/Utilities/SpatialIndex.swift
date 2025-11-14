//
//  SpatialIndex.swift
//  RecreatePhoto
//
//  Spatial indexing for efficient proximity queries
//

import Foundation
import CoreLocation

/// Simple grid-based spatial index for fast proximity queries
class SpatialIndex {
    private var grid: [GridKey: [PhotoLocation]] = [:]
    private let cellSize: Double = 0.01 // Approximately 1km at equator

    struct GridKey: Hashable {
        let latCell: Int
        let lonCell: Int

        init(latitude: Double, longitude: Double, cellSize: Double) {
            self.latCell = Int(floor(latitude / cellSize))
            self.lonCell = Int(floor(longitude / cellSize))
        }
    }

    init(photos: [PhotoLocation]) {
        buildIndex(photos: photos)
    }

    private func buildIndex(photos: [PhotoLocation]) {
        grid.removeAll()

        for photo in photos {
            let key = GridKey(latitude: photo.latitude, longitude: photo.longitude, cellSize: cellSize)
            grid[key, default: []].append(photo)
        }
    }

    /// Find all photos within a given radius of a location
    func findNearby(location: CLLocation, radiusMeters: Double) -> [PhotoLocation] {
        let lat = location.coordinate.latitude
        let lon = location.coordinate.longitude

        // Calculate how many cells we need to check
        // At worst case (equator), 1 degree ≈ 111km
        let latDelta = Int(ceil(radiusMeters / (111_000 * cellSize))) + 1
        let lonDelta = Int(ceil(radiusMeters / (111_000 * cellSize * cos(lat * .pi / 180)))) + 1

        let centerKey = GridKey(latitude: lat, longitude: lon, cellSize: cellSize)

        var candidates: [PhotoLocation] = []

        // Check neighboring cells
        for latOffset in -latDelta...latDelta {
            for lonOffset in -lonDelta...lonDelta {
                let key = GridKey(
                    latitude: Double(centerKey.latCell + latOffset) * cellSize,
                    longitude: Double(centerKey.lonCell + lonOffset) * cellSize,
                    cellSize: cellSize
                )

                if let photos = grid[key] {
                    candidates.append(contentsOf: photos)
                }
            }
        }

        // Filter by actual distance
        return candidates.filter { photo in
            let photoLocation = CLLocation(latitude: photo.latitude, longitude: photo.longitude)
            return location.distance(from: photoLocation) <= radiusMeters
        }.sorted { photo1, photo2 in
            let dist1 = location.distance(from: photo1.location)
            let dist2 = location.distance(from: photo2.location)
            return dist1 < dist2
        }
    }

    /// Get count of indexed photos
    var count: Int {
        grid.values.reduce(0) { $0 + $1.count }
    }
}
